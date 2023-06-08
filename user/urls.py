from django.urls import path
from .views import *


urlpatterns = [
    path('assets', AssetsAPIView.as_view()),
    path('assets/<int:id>', AssetsAPIView.as_view()),
    path('staff',StaffAPIView.as_view()),
    path('staff/<int:id>',StaffAPIView.as_view()),
    path('order',OrderAPIView.as_view()),
    path('checkauth',CheckAuthView.as_view()),
    path('order-history/', OrderHistoryAPIView.as_view(), name='order-history'),
    path('transactions', TransactionsAPIView.as_view(), name='order-history'),
    path('populateorder',PopulateOrder.as_view())
]
