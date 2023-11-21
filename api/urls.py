from django.urls import path
import views
app_name = 'api'

url_patterns = [
    path('create', views.CreateUserView.as_view(), name='create'),
    path('me/', views.ManagerUserAPiView.as_view(), name='me')
]
