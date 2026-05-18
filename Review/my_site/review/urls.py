from django.urls import path
from . import views

urlpatterns = [
    path('', views.BaseView.as_view(), name='review-home'),
    path('restaurants', views.RestaurantListView.as_view(), name = 'restaurants'),
    path('restaurants/<int:pk>/', views.RestaurantDetailView.as_view(), name = 'restaurant-detail'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('logout/', views.LogoutUserView.as_view(), name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('delete/<int:pk>/', views.delete_review, name='delete_review')
]