from django.urls import path
from .views import *


urlpatterns = [
    # path('staff',StaffAPIView.as_view()),
    path('all-orders',AllOrdersHistory.as_view()),
    # path('romulus-assets/<str:type>', RomulusAssetsView.as_view()),
    path('romulus-assets', RomulusAssetsView.as_view()),
    path('start-delivery',DeliveryView.as_view()),
    path('delivery-data/<int:id>',DeliveryDataView.as_view()),
    path('order-distribution',OrderDistributionView.as_view()),
    path('order-distribution/<int:delivery_id>',OrderDistributionView.as_view()),
    path('finish-delivery/<int:delivery_id>',FinishDeliveryView.as_view()),
    path('finish-delivery',FinishDeliveryView.as_view()),
    path('checkauth',CheckAuthView.as_view()),
]