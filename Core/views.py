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
from user.serializers import PaymentSerializer
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
        user = get_object_or_404(User, pk=pk)
        user.delete()
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
        loc_data = AssetLocations.objects.filter(company=id)
        serializer = LocationSerializer(loc_data,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def delete(self,request,id):
        try:
            obj = AssetLocations.objects.get(id=id)
            obj.delete()
            return Response(200)
        except:
            return Response(500)



class AddPayment(APIView):
    def post(self, request):
        amount = request.data['payment_price']
        company = request.data['company']
        company_instance = User.objects.get(id=company)

        if int(company_instance.total_outstanding) < int(amount):
            return Response(data=f"Company ({company_instance.username}) outstanding amount is less than the entered amount", status=status.HTTP_400_BAD_REQUEST)
        
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                serializer.save()
                company_instance.total_outstanding -= int(amount)
                company_instance.save()
            return Response(data='Payment added successfully', status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyPaginator(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class AllOrdersHistory(APIView):
    pagination_class = MyPaginator
    permission_classes = [IsAdmin]

    def get(self, request):
        order_status = request.query_params.get('order_status')
        # company_id = request.query_params.get('company_id')
        order_type = request.query_params.get('order_type')
        
        if order_status:
            queryset = Order.objects.filter(order_type=order_type,order_status=order_status).order_by('-id')
        else:
            queryset = Order.objects.filter(order_type=order_type,).order_by('-id')

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = OrderSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

class OrderStatus(APIView):
    permission_classes = [AllowAny]
    def post (self, request,id):
        order_status = request.data['order_status']
        order = Order.objects.get(id=id)
        
        if order_status == order.order_status:
            return Response(500)
        
        company = order.company
        if order.order_status == 'Delivered':
            # prev_payment = Payments.objects.get(order=order.id)
            prev_payment = Payments.objects.get(Q(order=order.id) & Q(is_active=True))
            prev_payment.delete()
            
            company.total_outstanding = company.total_outstanding - order.total_price
            company.total_purchase_cost =  company.total_purchase_cost - order.total_price
            company.total_purchase_quantity = company.total_purchase_quantity - order.quantity
            company.save()

        order.order_status = order_status
        order.save()
        if order_status == 'Delivered':
            payment_data = {
                    'company': order.company.id,
                    'payment_type': 'purchase',
                    'payment_price': order.total_price,
                    'order':order.id,
                    'payment_method': '',  # Add your payment method here
                    'created_month':timezone.now().strftime('%B')
                }
                
            payment_serializer = PaymentSerializer(data=payment_data)
            if payment_serializer.is_valid():
                payment_serializer.save()

                company.total_outstanding = (company.total_outstanding or 0) + order.total_price
                company.total_purchase_cost =  (company.total_purchase_cost or 0) + order.total_price
                company.total_purchase_quantity = (company.total_purchase_quantity or 0) + order.quantity
                company.save()
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


    

class SampleGet(APIView):
    def get(self,request):
        tk=request.COOKIES.get('token')
        print(tk)
        return Response(200)


