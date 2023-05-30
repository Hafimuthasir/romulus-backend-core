from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from rest_framework import status
from .models import Company
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
        company = Company.objects.exclude(is_admin=True)
        serializer = CompanySerializer(company,many=True)
        return Response(status=status.HTTP_200_OK,data=serializer.data)
    
    @csrf_exempt
    def delete(self, request, pk):
        print(pk)
        company = get_object_or_404(Company, pk=pk)
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
            )

            res.set_cookie(
            key='refresh_token',
            value=str(refresh_token),
            httponly=True,
            )
            
            res.data = str(refresh_token.access_token)
            res["X-CSRFToken"] = csrf.get_token(request)
            return res

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class CheckAuthView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
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
    

class SampleGet(APIView):
    def get(self,request):
        tk=request.COOKIES.get('token')
        print(tk)
        return Response(200)


