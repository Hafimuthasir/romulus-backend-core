from Core.models import *
from Core.serializers import *
from user.serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
import traceback
from django.shortcuts import get_object_or_404

class MyPaginator(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class OrderHistoryCommonView(APIView):
    pagination_class = MyPaginator
   

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
    

class AssetsCommonView(APIView):

    def post(self,request):
        serializer = AssetsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE,data={'message':serializer.errors,'status':False})
        return Response(status=status.HTTP_201_CREATED,data={'message':'Success','status':True})
    
    def get(self,request,id):
        try:
            data = Assets.objects.filter(company_id=id,is_active=True).order_by('-id')
            serializer=AssetsSerializer(data,many=True)
            return Response(serializer.data)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,data={'message':'Something Went Wrong','status':False})
        
    def put(self, request, id):
        try:
            asset = Assets.objects.get(id=id)
            serializer = AssetsSerializer(asset, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_200_OK, data={'message': 'Success', 'status': True})
            else:
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data={'message': serializer.errors, 'status': False})
        except Assets.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Asset not found', 'status': False})
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={'message': 'Something Went Wrong', 'status': False})


    def delete(self,request,id):
        data = Assets.objects.get(id=id)
        data.delete()
        return Response(200)
    


class OrderCommonView(APIView):

    def post(self, request): 
        print(request.data)
        company_info = CompanyInfo.objects.get(company_id=request.data['company'])
        
        if request.data['diesel_price'] != company_info.diesel_price or request.data['discount_price'] != company_info.discount_price:
            return Response({'message':'Diesel Price Has Been Updated...Refreshing Page'},status=status.HTTP_409_CONFLICT)
        
        
        # if not request.data['bypass_totalizer']:
        #     asset = Assets.objects.get(id=request.data['asset'])
        #     last_totalizer = asset.totalizerreadings_set.last()
        #     print(last_totalizer)
        #     if last_totalizer:
        #         ist_tz = pytz.timezone('Asia/Kolkata')
        #         ist_created_at = last_totalizer.created_at.astimezone(ist_tz).date()
        #         today = timezone.now().astimezone(ist_tz).date()
        #         if ist_created_at != today:
        #             print('looop')
        #             return Response({'message':'Totalizer Is Not Updated Today'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        saved_amount = float(request.data['requested_quantity']) * float(company_info.discount_price)
        request.data['discount_price'] = company_info.discount_price
        request.data['saved_amount'] = saved_amount
        serializer = OrderSerializer(data=request.data)  
        if serializer.is_valid():
            order = serializer.save()
            try:
                company_info = CompanyInfo.objects.get(company=order.company)
                print('1111',company_info)
                saved_amount = order.requested_quantity * company_info.discount_price
                order.discount_price = company_info.discount_price
                order.saved_amount = saved_amount
                order.requested_total_price = order.requested_total_price
                order.save()
                
                try:
                    subject = 'Romulus Order Update !!'
                    recipient_email = 'muthasirhafi@gmail.com'
                    orders_url = 'http://localhost:3000/orders'
                    message = f"New order with ID {order.id} has been placed by company '{order.company.username}'. You can view your orders here: {orders_url}"

                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email])

                    # return Response({'message': 'Order placed successfully'}, status=status.HTTP_201_CREATED)
                except Exception as e:
                        traceback.print_exc() 


                return Response({'message': 'Order placed successfully'}, status=status.HTTP_201_CREATED)
            except:
                order.delete()
                return Response({'message':'errored'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        

            # # Create payment entry
            # payment_data = {
            #     'company': order.company.id,
            #     'payment_type': 'purchase',
            #     'payment_price': order.total_price,
            #     'order':order.id,
            #     'payment_method': '',  # Add your payment method here
            #     'created_month':timezone.now().strftime('%B')
            # }
            
            # payment_serializer = PaymentSerializer(data=payment_data)
            # company = order.company
            # company.total_outstanding = (company.total_outstanding or 0) + order.total_price
            # company.total_purchase_cost =  (company.total_purchase_cost or 0) + order.total_price
            # company.total_purchase_quantity = (company.total_purchase_quantity or 0) + order.quantity
            # company.save()

            # print(company.total_outstanding)
            # if payment_serializer.is_valid():
            #     with transaction.atomic():
            #         payment_serializer.save()
            #         return Response({'message': 'Order placed successfully'}, status=status.HTTP_201_CREATED)
            # else:
            #     order.delete()
            #     print(payment_serializer.errors)
            #     return Response(payment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TransactionsCommonView(APIView):
    pagination_class = MyPaginator

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
    

class GetDieselPrice(APIView):
    
    def get(self, request, id):
        try :
            instance = CompanyInfo.objects.get(company_id = id)
            data = {'diesel_price':instance.diesel_price,'discount':instance.discount_price}

            return Response(data,status=200)
        except:
            return Response(500)
    

class StaffCommonView(APIView):

    def post(self, request):
        serializer = StaffSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Staff added successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, id):
        staff_only = request.query_params.get('staff_only')
        if staff_only :
            staff_members = User.objects.filter(company_id=id,role='staff',is_active=True).order_by('username')
        else:
            staff_members = User.objects.filter(company_id=id,is_active=True).order_by('username')
        serializer = GetStaffSerializer(staff_members, many=True)
        return Response(serializer.data)
    
    def put(self, request, id):
        user = get_object_or_404(User, pk=id)
        serializer = StaffSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Staff updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, id):
        instance = get_object_or_404(User, id=id)
        password = request.data.get('password')
        if password:
            instance.password = make_password(password)
            instance.save()
            return Response({'message': 'Password changed successfully'})
        return Response({'message': 'No password provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        user = User.objects.get(id=id)
        user.delete()
        return Response({'Deleted Sucessfully'},status=status.HTTP_200_OK)
    