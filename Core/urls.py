from django.urls import path
from .views import *


urlpatterns = [
    path('company',CompanyCred.as_view()),
    path('company/<int:pk>',CompanyCred.as_view()),
    path('login',CompanyLoginView.as_view()),
    path('checkauth',CheckAuthView.as_view()),
    path('location',AssetLocationsView.as_view()),
    path('location/<id>',AssetLocationsView.as_view()),
    path('sampleget',SampleGet.as_view()),
]
