from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/',  auth_views.LoginView.as_view(template_name='login.html'),  name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.homeView, name='home'),
    path('<int:hotel_id>/', views.hotelDetailView, name='hotel_detail'),
    path('profile/', views.profileView, name='profile'),
    path('profile/edit/', views.profileEditView, name='profile_edit'),
    path('roomtype/<int:room_type_id>/book/', views.roomTypeBookView, name='room_type_book'),
    path('my-reservations/', views.myReservationsView, name='my_reservations'),
    path('reservation/<int:pk>/cancel/', views.reservationCancelView, name='reservation_cancel'),
    path('hotel/<int:hotel_id>/review/', views.reviewCreateView, name='review_create'),
    path('all-reservations/', views.allReservationsView, name='all_reservations'),
    path('reservation/<int:pk>/set-status/<str:new_status>/', views.reservationSetStatusView, name='reservation_set_status'),
    path('reservation/<int:pk>/edit/', views.reservationEditView, name='reservation_edit'),
    path('review/<int:pk>/delete/', views.reviewDeleteView, name='review_delete'),
    path('monthly-guests/', views.monthlyGuestsView, name='monthly_guests'),
    path('search/', views.searchView, name='search'),
]