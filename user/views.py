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
        try:
            data = Assets.objects.get(id=id)
            data.delete()
            return Response(200)
        except:
            return Response('something went wrong',status=status.HTTP_500_INTERNAL_SERVER_ERROR,)
    

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
                'payment_method': '',  # Add your payment method here
                'created_month':timezone.now().strftime('%B')
            }
            
            payment_serializer = PaymentSerializer(data=payment_data)
            company = order.company
            company.total_outstanding = company.total_outstanding + order.total_price
            company.total_purchase_cost =  company.total_purchase_cost + order.total_price
            company.total_purchase_quantity = company.total_purchase_quantity + order.quantity
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
        

        if order_status:
            queryset = Order.objects.filter(order_status=order_status).order_by('-created_at')
        else:
            queryset = Order.objects.all().order_by('-created_at')

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
            queryset = Payments.objects.filter(payment_type=payment_type,company=company).order_by('-created_at')
        else:
            queryset = Payments.objects.filter(company=company).order_by('-created_at')

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = PaymentSerializer(paginated_queryset, many=True)
        
        return paginator.get_paginated_response(serializer.data)
    

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