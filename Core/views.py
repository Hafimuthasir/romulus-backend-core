from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from rest_framework import status
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django.middleware import csrf
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from .cookie_auth import CookieJWTAuthentication
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework.generics import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions
from .models import Assets
from .serializers import AssetsSerializer
# from user.serializers import PaymentSerializer
from django.db import transaction
from user.serializers import OrderSerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from rest_framework.permissions import BasePermission
from romulus_admin.common_views import *
from romulus_admin.custom_permissions import IsAdmin

# Create your views here.

class CompanyCred(APIView):
    permission_classes = [IsAdmin]
    def post(self,request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            request.data['company'] = user.id
            # print('bbbb',request.data)
            info_serializer = CompanyInfoSerializer(data=request.data)            
            if info_serializer.is_valid():
                info_serializer.save()
                return Response(status=status.HTTP_201_CREATED,data={'message':'Success','status':True})
            user.permanent_delete()           
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE,data={'message':info_serializer.errors,'status':False})
        print(serializer.errors)
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE,data={'message':serializer.errors,'status':False})
        # else:
        #     return Response(status=status.HTTP_406_NOT_ACCEPTABLE,data={'message':serializer.errors,'status':False})
        
    
    def get(self,request):
        company = User.objects.filter(role='company').exclude(is_admin=True).exclude(is_active=False)
        serializer = GetCompanySerializer(company,many=True)
        return Response(status=status.HTTP_200_OK,data=serializer.data)
    

    @csrf_exempt
    def delete(self, request, pk):
        print(pk)
        company = get_object_or_404(User, pk=pk)
        employees = User.objects.filter(company_id=company)
        
        for employee in  employees :
            employee.delete()

        company.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class CompanyLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = CompanyLoginSerializer(data=request.data)
        if serializer.is_valid():
            company = serializer.validated_data['company']
            refresh_token = RefreshToken.for_user(company)

            response_data = {
                'message': 'Login successful',
                'user': {
                    'id': company.id,
                    'username': company.username,
                    # Include any other user information you need
                }
            }
            res= Response()
            res.set_cookie(
            key='access_token',
            value=str(refresh_token.access_token),
            httponly=True,  
            samesite='None',   
            secure=True
            )

            res.set_cookie(
            key='refresh_token',
            value=str(refresh_token),
            httponly=True,
            samesite='None',
            secure=True
            )
            

            res.data = str(refresh_token.access_token)
            res["X-CSRFToken"] = csrf.get_token(request)
            return res

        error = list(serializer.errors.values())[0][0]
        print(error)
        return Response(error, status=status.HTTP_400_BAD_REQUEST)
    

class CompanyLogoutView(APIView):
    # permission_classes = [AllowAny]
    def get(self, request):
        # Clear the access_token and refresh_token cookies by setting their values to empty
        res = JsonResponse({'message': 'Logout successful'})
        # response.set_cookie('access_token', '', max_age=0, secure=True)
        # response.set_cookie('refresh_token', '', max_age=0, secure=True)
        res.set_cookie(
            key='access_token',
            value='',
            httponly=True,  
            samesite='None',   
            secure=True,
            max_age=0,
            )

        res.set_cookie(
            key='refresh_token',
            value='',
            httponly=True,
            samesite='None',
            secure=True,
            max_age=0
            )
        
        return res
    
# class IsAdmin(BasePermission):
#     def has_permission(self, request, view):
#         authorization_header = request.META['HTTP_AUTHORIZATION']
        
#         if authorization_header:
#             token_type, access_token = authorization_header.split()

#             jwt_auth = JWTAuthentication()     
#             payload = jwt_auth.get_validated_token(access_token)
#             user = jwt_auth.get_user(payload)  
#             if user.is_authenticated:
#                 if user.is_admin:
#                     return True
    
        # return False 
    
class CheckAuthView(APIView):
    # authentication_classes = [JWTAuthentication]    
    permission_classes = [IsAdmin]
   
    # permission_classes = [AllowAny]

    def get(self, request):
        user = request.user
        response_data = {
            'message': 'Authentication successful',
            'user': {
                'id': user.id,
                'username': user.username,
                # 'user_type': user.user_type,
                # 'company_id':user.company_id
                # Include any other user information you need
            }
        }
        return Response(response_data,status=status.HTTP_200_OK)
    


class AssetLocationsView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(200)
        print(serializer.errors)
        return Response(500)
    
    def get(self,request,id):
        loc_data = ClientLocations.objects.filter(company=id)
        serializer = LocationSerializer(loc_data,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def delete(self,request,id):
        try:
            obj = ClientLocations.objects.get(id=id)
            obj.delete()
            return Response(200)
        except:
            return Response(500)



# This View, BASED MODEL AND serializeR ARE NOT USING NOW NEED TO CLEAN IT
# *************
# *************
# *************
# *************
class AddPayment(APIView):
    def post(self, request):
        amount = request.data['payment_price']
        company = request.data['company']
        company_instance = CompanyInfo.objects.get(company=company)
        print('111111111',company_instance.trade_name)

        if int(company_instance.total_outstanding) < int(amount):
            
            return Response(data="Company outstanding amount is less than the entered amount", status=status.HTTP_400_BAD_REQUEST)
        
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            
            with transaction.atomic():
                serializer.save()
                company_instance.total_outstanding -= int(amount)
                company_instance.save()
            return Response(data='Payment added successfully', status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyPaginator(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class AllOrdersHistory(APIView):
    pagination_class = MyPaginator
    permission_classes = [IsAdmin]

    def get(self, request):
        print('fefefeef')
        order_status = request.query_params.get('order_status')
        # company_id = request.query_params.get('company_id')
        order_type = request.query_params.get('order_type')
        
        
        if order_status:
            if order_type == 'all':
                queryset = Order.objects.filter(order_status=order_status).order_by('-id')
            else:
                queryset = Order.objects.filter(order_type=order_type,order_status=order_status).order_by('-id')
            
        else:
            queryset = Order.objects.all().order_by('-id')

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = OrderSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

class OrderStatus(APIView):
    permission_classes = [AllowAny]
    def put (self, request,id):
        order_status = request.data['order_status']
        order = Order.objects.get(id=id)
        
        if order_status == order.order_status:
            return Response(500)
        
        
        comp = order.company
        company = CompanyInfo.objects.get(company=comp)
        print('fff',company.total_outstanding)
        # if order.order_status == 'Delivered':
        #     # prev_payment = Payments.objects.get(order=order.id)
        #     print('hello',order.id)
        #     prev_payment = Payments.objects.get(order=order.id, is_active=True)
        #     prev_payment.delete()
            
        #     company.total_outstanding = company.total_outstanding - order.total_price
        #     company.total_purchase_cost =  company.total_purchase_cost - order.total_price
        #     company.total_purchase_quantity = company.total_purchase_quantity - order.quantity
        #     company.save()

        order.order_status = order_status
        if order_status == 'Approved':
            order.approved_quantity = request.data['approved_qty']
            order.order_status
            
        order.save()
        # return Response(200)

        # if order_status == 'Delivered':
        #     payment_data = {
        #             'company': order.company.id,
        #             'payment_type': 'purchase',
        #             'payment_price': order.total_price,
        #             'order':order.id,
        #             'payment_method': '',  # Add your payment method here
        #             'created_month':timezone.now().strftime('%B')
        #         }
                
        #     payment_serializer = PaymentSerializer(data=payment_data)
        #     if payment_serializer.is_valid():
        #         payment_serializer.save()

        #         company.total_outstanding = (company.total_outstanding or 0) + order.total_price
        #         company.total_purchase_cost =  (company.total_purchase_cost or 0) + order.total_price
        #         company.total_purchase_quantity = (company.total_purchase_quantity or 0) + order.quantity
        #         company.save()

        return Response(200)
    

class FuelPriceChange(APIView):
    def put(self,request):
        print('hai',request.data)
        change_type = request.data['change_type']
        if change_type == 'diesel':
            
            new_price = request.data['diesel_Price']
            company_id = request.data['company_id']
            try :
                instance = CompanyInfo.objects.get(company_id = company_id)
                instance.diesel_price = new_price
                instance.save()
                return Response(data='Diesel Price Updated Successfully', status=status.HTTP_200_OK)
            except :
                return Response(400)
            
        if change_type == 'discount':
            new_price = request.data['discount_price']
            company_id = request.data['company_id']
            try :
                instance = CompanyInfo.objects.get(company_id = company_id)
                instance.discount_price = new_price
                instance.save()
                return Response(data='Discount Price Updated Successfully', status=status.HTTP_200_OK)
            except :
                return Response(400)
        return Response(400)
            


class OrderHistoryAdmin(OrderHistoryCommonView):
    permission_classes = [IsAdmin]


class AssetsView(AssetsCommonView):
    permission_classes = [IsAdmin]

class OrderView(OrderCommonView):
    permission_classes = [IsAdmin]

class TransactionsView(TransactionsCommonView):
    permission_classes = [IsAdmin]

class GetDieselPrice(GetDieselPrice):
    permission_classes = [IsAdmin]
    

class RomulusAssetsView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        assets = RomulusAssets.objects.filter(is_active=True)
        serializer = RomulusAssetsSerializer(assets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = RomulusAssetsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TotalizerView(APIView):
    def post(self, request):
        print('ggggggg')
        serializer = TotalizerReadingsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(200)
        print(serializer.errors)
        return Response(500,status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class StaffAPIView(StaffCommonView):
    permission_classes = [IsAdmin]

    def get(self, request):
        
        staff_members = User.objects.filter(role='romulus_staff',is_active=True).order_by('username')
        serializer = GetStaffSerializer(staff_members, many=True)
        return Response(serializer.data)
    
class OrderDetailsView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request,order_id):
        order = Order.objects.get(id=order_id)
        serializer = OrderDetailsSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CompleteOrderView(APIView):
    permission_classes = [IsAdmin]
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            # serializer = OrderDetailsSerializer(order)
            deliveries = RomulusDeliveries.objects.filter(order_id=order_id)
            status_check = True
            

            for delivery in deliveries:
                if delivery.status == 'ongoing':
                    print('llllllll')
                    return Response(data='Finish or Cancel Ongoing Deliveries First..!!!',status=status.HTTP_400_BAD_REQUEST)
            
            company_info = CompanyInfo.objects.get(company=order.company.id)
            
            actual_price = company_info.diesel_price - company_info.discount_price
            order.order_status = 'Completed'
            if order.order_type == 'client':
                order.delivered_cost = order.requested_total_price
                order.delivered_quantity = order.requested_quantity
                order.saved_amount = order.requested_quantity * company_info.discount_price
            else:
                
                order.delivered_cost = (order.delivered_quantity or 0) * actual_price
                order.saved_amount = (order.delivered_quantity or 0) * company_info.discount_price
                
            
            order.is_billable = request.data['is_billable']
            
            order.save()
            return Response(data='Success', status=status.HTTP_200_OK)
        except Exception as e:
            return Response('Something went wrong',status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RemoveDistribution(APIView):
    @transaction.atomic
    def delete(self, request, id):
        try:
            distribution = OrderDistribution.objects.get(id = id)
            delivery = distribution.delivery
            order = delivery.order
            if order.billed :
                print('never if',order.billed)
                return Response(data='Cannot Remove...!! Order is Already Billed. Remove Invoice First',status=400)
            distribution.delete()
            
            if delivery.status == 'completed':
                print('delivery if')
                total_qty = OrderDistribution.objects.filter(delivery=delivery).aggregate(Sum('quantity'))['quantity__sum']
                delivery.quantity = total_qty
                delivery.save()
            order_total_qty = 0
            all_deliveries = RomulusDeliveries.objects.filter(order=order)

            for deliver in all_deliveries:
                if deliver.status == 'completed':
                    print('order if')
                    order_total_qty += deliver.quantity
            
            # all
            order.delivered_quantity = order_total_qty
            
            if order.order_status == 'Completed':
                print('order_completed if')
                company = CompanyInfo.objects.get(company=order.company)
                actual_price = company.diesel_price - company.discount_price
                order.delivered_cost = order_total_qty * actual_price
                order.saved_amount = order_total_qty * company.discount_price
            order.save()
            return Response(200)
        except:
            return Response(500)


class RemoveDelivery(APIView):
    @transaction.atomic
    def delete(self, request, id):
        try:
            delivery_instance = RomulusDeliveries.objects.get(id=id)
            # distribution = OrderDistribution.objects.get(id = id)
            # delivery = distribution.delivery
            order = delivery_instance.order
            if order.billed :
                print('never if',order.billed)
                return Response(data='Cannot Remove...!! Order is Already Billed. Remove Invoice First',status=400)
            # distribution.delete()
            # delivery.delete()
            disribution = OrderDistribution.objects.filter(delivery=delivery_instance)
            for dist in disribution :
                dist.delete()
            delivery_instance.delete()
            
            # if delivery.status == 'completed':
            #     print('delivery if')
            #     total_qty = OrderDistribution.objects.filter(delivery=delivery).aggregate(Sum('quantity'))['quantity__sum']
            #     delivery.quantity = total_qty
            #     delivery.save()

            order_total_qty = 0
            all_deliveries = RomulusDeliveries.objects.filter(order=order)

            for deliver in all_deliveries:
                if deliver.status == 'completed':
                    print('order if')
                    order_total_qty += deliver.quantity
            
            # all
            order.delivered_quantity = order_total_qty
            
            if order.order_status == 'Completed':
                print('order_completed if')
                company = CompanyInfo.objects.get(company=order.company)
                actual_price = company.diesel_price - company.discount_price
                order.delivered_cost = order_total_qty * actual_price
                order.saved_amount = order_total_qty * company.discount_price
            order.save()
            return Response(200)
        except:
            return Response(500)


class RemoveOrder(APIView):
    def delete(self,request,id):
        order = Order.objects.get(id=id)
        if order.billed:
            return Response(data='Cannot Remove...!! Order is Already Billed. Remove Invoice First',status=400)
        try:
            deliveries = RomulusDeliveries.objects.get(order=order)
            for delivery in deliveries:
                distributions = OrderDistribution.objects.filter(delivery=delivery)
                for distribution in distributions:
                    distribution.delete()
                delivery.delete()
            order.delete()
        except:
            order.delete()
        return Response(200)


class InvoiceView(APIView):
    def post(self, request, format=None):
        print('dsfdsfdsfsdffds')
        serializer = InvoiceSerializer(data=request.data)
        if serializer.is_valid():
            print('yoyo') 
            try:
                with transaction.atomic():  
                    invoice = serializer.save()    
                    order = invoice.order
                    order.billed = True
                    order.save()
                    company = CompanyInfo.objects.select_for_update().get(company=order.company)  # Use select_for_update to lock the company row during the transaction
                    company.total_outstanding += int(invoice.amount)
                    company.save()
                    transaction_instance = Transaction(transaction_type='Purchase',invoice=invoice,company_id=invoice.company_id)
                    transaction_instance.save()
            except Exception as e:
                print(f"Exception occurred: {e}")
                # If any part of the transaction fails, the changes will be rolled back
                # Handle the exception or log it as needed
                return Response({'error': 'Transaction failed.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # def get(self,request):
    #     instance = Invoice.objects.all().order_by('-id')
    #     serializer = InvoiceSerializer(instance,many=True)
    #     return Response (serializer.data)
    
class GetInvoices(GetInvoiceCommonView):
    permission_classes = [IsAdmin]
    




class InvoiceCompanies(APIView):
    permission_classes = [IsAdmin]  
    def get(self,request):
        # instances = Invoice.objects.filter(payment_status='Pending').values('company').distinct()
        company = User.objects.filter(role='company',is_active=True)
        serializer = UserSerializer(company,many=True)
        # print(serializer.data)
        return Response(serializer.data)
    

class IncompleteInvoiceByCompany(APIView):
    permission_classes = [IsAdmin]  
    def get(self,request,id ):
        instances = Invoice.objects.filter(company=id, payment_status__in=['Pending', 'Partial']).order_by('invoice_date')
        # instances = User.objects.filter(role='company',is_active=True)
        serializer = InvoiceSerializer(instances,many=True)
        # print(serializer.data)
        return Response(serializer.data)
    

class UnbilledOrders(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        orders = Order.objects.filter(order_status='Completed', billed=False, is_billable=True)
        serializer = OrderDetailsSerializer(orders,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class AddPaymentView(APIView):
    permission_classes = [IsAdmin]
    def post(self, request):
        company = request.data.get('company')
        payment_datetime = request.data.get('payment_datetime')
        payment_method = request.data.get('payment_method')
        transaction_id = request.data.get('transaction_id')
        amount = request.data.get('payment_amount')
        full_payment_invoices = request.data.get('full_payment_invoices')
        partial_payment_invoice = request.data.get('partial_payment_invoice')
        partial_amount = request.data.get('partial_amount')

        full_pay_instances = Invoice.objects.filter(id__in=full_payment_invoices)
        total_check = 0
        for invoice in full_pay_instances :
            total_check += invoice.get_pending_amount()
        print('12212121',partial_amount)
        if partial_payment_invoice:
            partial_instance = Invoice.objects.get(id=partial_payment_invoice)
            if partial_amount > partial_instance.get_pending_amount():
                return Response(500)
            total_check += partial_amount
        
        
        if int(total_check) == int(amount):
            print('level 0')
 
            serializer = InvoicePaymentSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    with transaction.atomic():
                        print('level 1')
                        payment = serializer.save()

                        for invoice in full_pay_instances:
                            invoice.payment_status = 'Paid'
                            invoice.paid_amount = invoice.amount
                            invoice.save()

                        if partial_payment_invoice:
                            partial_instance.payment_status = 'Partial'
                            partial_instance.paid_amount += partial_amount
                            partial_instance.save()
                        try:
                            transaction_instance = Transaction(transaction_type='Payment',payment=payment,company_id=company)
                            transaction_instance.save()
                        except Exception as e:
                            print('hello')
                        company = CompanyInfo.objects.select_for_update().get(company_id=company)  # Use select_for_update to lock the company row during the transaction
                        company.total_outstanding -= int(amount)
                        company.save()

                except Exception as e:
                    print(e)
                # If any part of the transaction fails, the changes will be rolled back
                # Handle the exception or log it as needed
                    return Response(status=500)
            # payment.company = 
            print(serializer.errors)
        print('req_amt :',amount,'check_amt :',total_check)
        return Response(500)


class InvoicePaymentView(GetPaymentsCommonView):
    permission_classes = [IsAdmin]
    



# class SampleGet(APIView):
    
#     def get(self,request):
#         tk=request.COOKIES.get('token')
#         print(tk)
#         return Response(200)


