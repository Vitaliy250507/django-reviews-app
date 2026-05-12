from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.views.generic import View
from .models import Restaurant
from django.shortcuts import render
# Create your views here.

class RestaurantListView(ListView):
    template_name = "reviews/restaurant_list.html"
    model = Restaurant
    context_object_name = "restaurants"

class BaseView(View):
    def get(self, request):
        return render(request, 'base.html')
    