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
        print('111',request.user)
        order_status = request.query_params.get('order_status')
        # company_id = request.query_params.get('company_id')
        order_type = request.query_params.get('order_type')
        # req_from = request.query_params.get('req_from') if 'req_from' in request.query_params else None
        
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
            delivery = RomulusDeliveries.objects.get((Q(staff_1=user) | Q(staff_2=user)) & Q(status='ongoing'))
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
    

class StartDeliveryView(APIView):
    permission_classes = [IsRomulusStaff]

    def get_is_totalizer_updated(self,asset):
        last_totalizer = asset.totalizerreadings_set.last()
        if last_totalizer:
            ist_tz = pytz.timezone('Asia/Kolkata')
            ist_created_at = last_totalizer.created_at.astimezone(ist_tz).date()
            today = timezone.now().astimezone(ist_tz).date()
            return ist_created_at == today
        return False
    
    def post(self,request):
        # print(request.data['bowser'])
        bowser = request.data['bowser']
        if not bowser:
            return Response(data='Select One Bowser...!!!',status=status.HTTP_400_BAD_REQUEST)

        bowser_instance = RomulusAssets.objects.get(id=bowser)
        totalizer_check = self.get_is_totalizer_updated(bowser_instance)
        if not totalizer_check :
            return Response(data='Totalizer is Not Updated Today For this Bowser...!!!',status=status.HTTP_400_BAD_REQUEST)
        # return Response(data='Delivery Started',status=status.HTTP_200_OK)
    
    
        serializer = DeliverySerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    order = Order.objects.select_for_update().get(id=request.data['order'])
                    serializer.save()
                    order.order_status = 'Delivering'
                    order.save()
                    return Response(data='Success', status=status.HTTP_201_CREATED)
            except Exception as e:
                print(e)
                return Response(data='Something Went Wrong', status=status.HTTP_400_BAD_REQUEST)
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
        # for i in distribution:
        #     total_qty += i.quantity
            # total_price += 
        # total_quantity = 
        print(total_qty)
        return Response(200)
    
    def post (self,request):
        
        if not request.data['totalizer_reading'] :
            return Response(data='Enter the Totalizer Reading',status=status.HTTP_400_BAD_REQUEST)
        try:
            with transaction.atomic():
                delivery = RomulusDeliveries.objects.get(id = request.data['delivery_id'])
                delivery.status= 'completed'
                total_qty = OrderDistribution.objects.filter(delivery=delivery).aggregate(Sum('quantity'))['quantity__sum']
                delivery.quantity = total_qty
                # print(request.data['bowser'])
                # delivery.bowser_id = int(request.data['bowser'])
                print(request.data['totalizer_reading'])
                delivery.totalizer = request.data['totalizer_reading']
                delivery.chalan_image = request.data['chalan_image']
                delivery.chalan_no = request.data['chalan_no']
                delivery.save()
                order = delivery.order
                order.order_status = 'Partial'
                order.delivered_quantity = order.delivered_quantity + total_qty if order.delivered_quantity else total_qty
                order.save()
                
                return Response(200)
        except Exception as e:
            print("fsdfsfdsfsdfsdfsfsdfds",e)
            return Response(data=e,status=status.HTTP_400_BAD_REQUEST)

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

    
class RomulusAssetsStaff(RomulusAssetsCommonView):
    permission_classes = [IsRomulusStaff]

class TotalizerView(APIView):
    permission_classes = [IsRomulusStaff]
    def post(self, request):
        print('ggggggg')
        serializer = TotalizerReadingsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(200)
        print(serializer.errors)
        return Response(500,status=status.HTTP_500_INTERNAL_SERVER_ERROR)
