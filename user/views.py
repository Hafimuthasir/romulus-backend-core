from django.shortcuts import render
from Core.serializers import AssetsSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from Core.models import Assets,Company
from .serializers import *


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