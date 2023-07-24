from django.urls import path
from .views import *


urlpatterns = [
    path('company',CompanyCred.as_view()),
    path('staff',StaffAPIView.as_view()),
    path('staff/<int:id>',StaffAPIView.as_view()),
    path('company/<int:pk>',CompanyCred.as_view()),
    path('login',CompanyLoginView.as_view()),
    path('logout',CompanyLogoutView.as_view(), name='logout'),
    path('checkauth',CheckAuthView.as_view()),
    path('location',AssetLocationsView.as_view()),
    path('location/<id>',AssetLocationsView.as_view()),
    path('add-payment',AddPayment.as_view()),
    path('all-orders',AllOrdersHistory.as_view()),
    path('change-orderstatus/<id>',OrderStatus.as_view()),
    path('fuel-price', FuelPriceChange.as_view()),
    path('get-diesel-price/<id>',GetDieselPrice.as_view()),
    path('order-history/', OrderHistoryAdmin.as_view()),
    path('assets', AssetsView.as_view()),
    path('assets/<int:id>', AssetsView.as_view()),
    path('order',OrderView.as_view()),
    path('transactions', TransactionsView.as_view()),
    path('romulus-assets', RomulusAssetsView.as_view()),
    path('order-details/<int:order_id>',OrderDetailsView.as_view()),
    path('totalizer', TotalizerView.as_view()),
    path('sampleget',SampleGet.as_view()),
]
