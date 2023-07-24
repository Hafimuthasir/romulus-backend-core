from django.shortcuts import render
from romulus_admin.common_views import *
from romulus_admin.custom_permissions import IsRomulusStaff
from Core.views import *
from .serializers import *
from django.db.models import Q

# Create your views here.

class AllOrdersHistory(APIView):
    pagination_class = MyPaginator
    permission_classes = [IsRomulusStaff]

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
    


class CheckAuthView(APIView):
    # authentication_classes = [JWTAuthentication]    
    permission_classes = [IsRomulusStaff]
   
    # permission_classes = [AllowAny]

    def get(self, request):
        user = request.user
        try:
            delivery = RomulusDeliveries.objects.get((Q(staff_1=user) | Q(staff_2=user)) & Q(status='open'))
        except :
            delivery = None

        print('deliveries',delivery)
        # deliveries_arr = []
        # for i in deliveries:
        #     deliveries_arr.append(i.id)
        response_data = {
            'message': 'Authentication successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'delivery_open':True if delivery else False,
                'delivery_id':delivery.id if delivery else None
                # 'user_type': user.user_type,
                # 'company_id':user.company_id
                # Include any other user information you need
            }
        }
        return Response(response_data,status=status.HTTP_200_OK)
    

class RomulusAssetsView(APIView):
    permission_classes = [IsRomulusStaff]
    def get(self, request):
        if 'type' in request.query_params:
            assets = RomulusAssets.objects.filter(asset_type = request.query_params['type'])
        else:
            assets = RomulusAssets.objects.all()
        serializer = RomulusAssetsSerializer(assets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = RomulusAssetsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class DeliveryView(APIView):
    permission_classes = [IsRomulusStaff]

    def post(self,request):
        serializer = DeliverySerializer(data=request.data)
        if serializer.is_valid():
            try:
                order = Order.objects.get(id=request.data['order'])
                serializer.save()
                order.order_status = 'Delivering'
                order.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class DeliveryDataView(APIView):
    permission_classes = [IsRomulusStaff]

    def get (self,request,id):
        delivery = RomulusDeliveries.objects.get(id=id)
        order = delivery.order
        client_assets = Assets.objects.filter(company = order.company, is_active=True)
        serializer = AssetsSerializer(client_assets,many=True)
        print('order',order)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

class OrderDistributionView(APIView):
    permission_classes = [IsRomulusStaff]

    def post(self,request):
        serializer = DistributionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(200)
        print(serializer.errors)
        # return Response(serializer.errors)

    def get(self, request, delivery_id):
        disribution = OrderDistribution.objects.filter(delivery=delivery_id)
        serializer = DistributionSerializer(disribution,many=True)
        return Response(serializer.data)
    

class FinishDeliveryView(APIView):
    permission_classes = [IsRomulusStaff]

    def get(self, request, delivery_id):
        delivery = RomulusDeliveries.objects.get(id=delivery_id)
        order_uid = delivery.order.order_id
        company_name = delivery.order.company.username
        distribution = delivery.orderdistribution_set.all()
        total_qty = 0
        total_price = 0
        # diesel_price = models.ForeignKey
        for i in distribution:
            total_qty += i.quantity
            # total_price += 
        # total_quantity = 
        print(total_qty)
        return Response(200)
    
    def post (self,request):
        delivery = RomulusDeliveries.objects.get(id = request.data['delivery_id'])
        delivery.status= 'completed'
        total_qty = delivery.orderdistribution_set.all().aggregate(Sum('quantity'))['quantity__sum']
        delivery.quantity = total_qty
        delivery.save()
        order = delivery.order
        order.order_status = 'Partial'
        order.save()
        return Response(200)

    # def post(self,request):
    #     serializer = DeliverySerializer(data=request.data)
    #     if serializer.is_valid():
    #         try:
    #             order = Order.objects.get(id=request.data['order'])
    #             serializer.save()
    #             order.order_status = 'Delivering'
    #             order.save()
    #             return Response(serializer.data, status=status.HTTP_201_CREATED)
    #         except:
    #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     print(serializer.errors)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    