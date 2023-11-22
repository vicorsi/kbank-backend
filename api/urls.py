from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('create', views.CreateUserView.as_view(), name='create'),
    path('me/', views.ManagerUserAPiView.as_view(), name='me')
]
