from django.urls import path
from .views import *


urlpatterns = [
    path('assets', AssetsAPIView.as_view()),
    path('assets/<int:id>', AssetsAPIView.as_view()),
    path('staff',StaffAPIView.as_view()),
    path('staff/<int:id>',StaffAPIView.as_view()),
]
