from django.shortcuts import render
from Core.serializers import AssetsSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from Core.models import Assets,Company
from .serializers import *
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from django.utils import timezone
from django.db import transaction
from Core.serializers import CompanyLoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Sum
from openpyxl import Workbook
from django.http import HttpResponse
import calendar
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter





# Create your views here.
class AssetsAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        serializer = AssetsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE,data={'message':serializer.errors,'status':False})
        return Response(status=status.HTTP_201_CREATED,data={'message':'Success','status':True})
    
    def get(self,request,id):
        try:
            data = Assets.objects.filter(company_id=id)
            print(data)
            serializer=AssetsSerializer(data,many=True)
            return Response(serializer.data)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,data={'message':'Something Went Wrong','status':False})
        

    def delete(self,request,id):
        # try:
        data = Assets.objects.get(id=id)
        data.delete()
        return Response(200)
        # except:
        #     return Response('something went wrong',status=status.HTTP_500_INTERNAL_SERVER_ERROR,)
    

class StaffAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = StaffSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Staff added successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, id):
        staff_members = Company.objects.filter(company_id=id)
        serializer = GetStaffSerializer(staff_members, many=True)
        return Response(serializer.data)
    

# class OrderAPIView(APIView):
#     permission_classes = [AllowAny]

#     def post(self,request):
#         serializer = OrderSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'message': 'Order placed successfully'})


class OrderAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()

            # Create payment entry
            payment_data = {
                'company': order.company.id,
                'payment_type': 'purchase',
                'payment_price': order.total_price,
                'order':order.id,
                'payment_method': '',  # Add your payment method here
                'created_month':timezone.now().strftime('%B')
            }
            
            payment_serializer = PaymentSerializer(data=payment_data)
            company = order.company
            company.total_outstanding = (company.total_outstanding or 0) + order.total_price
            company.total_purchase_cost =  (company.total_purchase_cost or 0) + order.total_price
            company.total_purchase_quantity = (company.total_purchase_quantity or 0) + order.quantity
            company.save()

            print(company.total_outstanding)
            if payment_serializer.is_valid():
                with transaction.atomic():
                    payment_serializer.save()
                    return Response({'message': 'Order placed successfully'}, status=status.HTTP_201_CREATED)
            else:
                order.delete()
                print(payment_serializer.errors)
                return Response(payment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyPaginator(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class OrderHistoryAPIView(APIView):
    pagination_class = MyPaginator
    permission_classes = [AllowAny]

    def get(self, request):
        order_status = request.query_params.get('order_status')
        company_id = request.query_params.get('company_id')
        order_type = request.query_params.get('order_type')
        
        if order_status:
            queryset = Order.objects.filter(company=company_id,order_type=order_type,order_status=order_status).order_by('-created_at')
        else:
            queryset = Order.objects.filter(company=company_id,order_type=order_type,).order_by('-created_at')

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = OrderSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)



class TransactionsAPIView(APIView):
    pagination_class = MyPaginator
    permission_classes = [AllowAny]

    def get(self, request):
        payment_type = request.query_params.get('payment_type')
        company = request.query_params.get('company_id')
        
        if payment_type:
            queryset = Payments.objects.filter(payment_type=payment_type, company=company).order_by('-created_at')
        else:
            queryset = Payments.objects.filter(company=company).order_by('-created_at')

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = PaymentSerializer(paginated_queryset, many=True)
        
        return paginator.get_paginated_response(serializer.data)


class DashboardView(APIView):
    permission_classes = [AllowAny] 
    def get(self,request,id):
        try : 
            current_month = datetime.now().month
            current_year = datetime.now().year

            total_price = Order.objects.filter(company=id,created_at__year=current_year, created_at__month=current_month).aggregate(total_price=Sum('total_price'))['total_price']
            total_quantity = Order.objects.filter(company=id,created_at__year=current_year, created_at__month=current_month).aggregate(total_quantity=Sum('quantity'))['total_quantity']

            company_obj = Company.objects.get(id=id)

            dashboard_data = {
                'monthly_purchase_cost' : total_price,
                'monthly_purchase_quantity' : total_quantity,
                'total_outstanding': company_obj.total_outstanding
            }

            return Response(data=dashboard_data,status=status.HTTP_200_OK)
        
        except:
            return Response('Something went wrong',status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExportOrdersView(APIView):
    permission_classes = [AllowAny] 

    def get(self, request):
        # Query the orders data from the database
        company_id = request.query_params.get('company_id')
        filter_type = request.query_params.get('filter_type')
        
        
        if filter_type == 'date_range':
            from_date = request.query_params.get('from_date')
            to_date = request.query_params.get('to_date')
            from_date = timezone.make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
            to_date = timezone.make_aware(datetime.strptime(to_date, '%Y-%m-%d'))
            orders = Order.objects.filter(company=company_id, created_at__range=[from_date, to_date])
        else:
            month = request.query_params.get('month')
            month_number = list(calendar.month_name).index(month.capitalize())
            orders = Order.objects.filter(company=company_id, created_at__month=month_number)

        # Create a new Excel workbook and worksheet
        wb = Workbook()
        ws = wb.active

        # Apply formatting to the headers
        header_font = Font(bold=True)
        for col_num, header in enumerate(['Order ID', 'Ordered By','User Type', 'Asset','Quantity', 'Total Price',  'Created At'], start=1):
            col_letter = get_column_letter(col_num)
            cell = ws['{}1'.format(col_letter)]
            cell.value = header
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')

        # Apply formatting to the order data
        for row_num, order in enumerate(orders, start=2):
            ws.cell(row=row_num, column=1, value=order.id)
            ws.cell(row=row_num, column=2, value=order.ordered_by.username)
            ws.cell(row=row_num, column=3, value=order.ordered_user_type)
            ws.cell(row=row_num, column=4, value=order.asset.assetName)
            ws.cell(row=row_num, column=5, value=order.quantity)
            ws.cell(row=row_num, column=6, value=order.total_price)
            ws.cell(row=row_num, column=7, value=order.created_at.astimezone(timezone.utc).replace(tzinfo=None))

        # Auto-size columns
        for col_num in range(1, 8):
            col_letter = get_column_letter(col_num)
            ws.column_dimensions[col_letter].auto_size = True
        
        ws.column_dimensions['G'].width = 20

        # Create the HTTP response with the Excel file content
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=orders.xlsx'

        # Save the workbook to the response
        wb.save(response)

        return response





# class UserLoginView(APIView):
#     permission_classes = [AllowAny]
#     def post(self, request):
#         serializer = CompanyLoginSerializer(data=request.data)
#         if serializer.is_valid():
#             company = serializer.validated_data['company']
#             refresh_token = RefreshToken.for_user(company)

#             response_data = {
#                 'message': 'Login successful',
#                 'user': {
#                     'id': company.id,
#                     'username': company.username,
#                     # Include any other user information you need
#                 }
#             }
#             res= Response()
#             res.set_cookie(
#             key='access_token',
#             value=str(refresh_token.access_token),
#             httponly=True,  
#             # samesite='None',   
#             secure=True
#             )

#             res.set_cookie(
#             key='refresh_token',
#             value=str(refresh_token),
#             httponly=True,
#             samesite='None',
#             secure=True
#             )
            
#             res.data = str(refresh_token.access_token)
#             res["X-CSRFToken"] = csrf.get_token(request)
#             return res

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CheckAuthView(APIView):
    authentication_classes = [JWTAuthentication]    
    permission_classes = [IsAuthenticated]
   
    # permission_classes = [AllowAny]

    def get(self, request):
        user = request.user
        response_data = {
            'message': 'Authentication successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'user_type': user.user_type,
                'company_id':user.company_id
                # Include any other user information you need
            }
        }
        return Response(response_data,status=status.HTTP_200_OK)







class PopulateOrder(APIView):
    def get(self,request):
        company = Company.objects.get(id=34)
        asset = Assets.objects.get(id=20)
        for i in range(50):
            order = Order.objects.create(
                company=company,
                ordered_by=company,
                quantity=10,
                asset=asset,
                diesel_price=3.5,
                total_price=35.0,
                order_status='ordered',
                created_at=timezone.now(),
                ordered_user_type='manager'
            )
        return Response(200)