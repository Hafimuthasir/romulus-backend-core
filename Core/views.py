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
# Create your views here.

class CompanyCred(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE,data={'message':serializer.errors,'status':False})
        return Response(status=status.HTTP_201_CREATED,data={'message':'Success','status':True})
    
    def get(self,request):
        company = User.objects.filter(role='company').exclude(is_admin=True).exclude(is_active=False)
        serializer = CompanySerializer(company,many=True)
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
    permission_classes = [AllowAny]

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
    

class SampleGet(APIView):
    def get(self,request):
        tk=request.COOKIES.get('token')
        print(tk)
        return Response(200)


