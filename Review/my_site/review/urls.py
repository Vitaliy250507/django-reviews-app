from django.urls import path
from . import views

urlpatterns = [
    path('', views.BaseView.as_view(), name='review-home'),
    path('restaurants', views.RestaurantListView.as_view(), name = 'restaurants'),
    path('restaurants/<int:pk>/', views.RestaurantDetailView.as_view(), name = 'restaurant-detail')
]