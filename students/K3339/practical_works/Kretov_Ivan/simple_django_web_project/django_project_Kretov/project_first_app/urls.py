from django.urls import path
from . import views

urlpatterns = [
    path('owner/<int:owner_id>/', views.owner_detail, name='owner_detail'),
    path('owner/list/', views.owner_list, name='owner_list'),
    path('owner/create/', views.create_owner, name='owner_create'),
    path('car/list/', views.CarListView.as_view(), name='car_list'),
    path('car/<int:pk>/', views.CarDetailView.as_view(), name='car_detail'),
    path('car/<int:pk>/edit/', views.CarUpdateView.as_view(), name='car_update'),
    path('car/create/', views.CarCreateView.as_view(), name='car_create'),
    path('car/<int:pk>/delete/', views.CarDeleteView.as_view(), name='car_delete'),
]