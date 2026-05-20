from django.contrib import messages
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.views.generic import View, TemplateView
from .models import Restaurant, Review
from .forms import LoginForm, ReviewForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.detail import DetailView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.db.models import Q
# Create your views here.

class RestaurantListView(ListView):
    template_name = "reviews/restaurant_list.html"
    model = Restaurant
    context_object_name = "restaurants"

    def get_queryset(self):
        queryset = Restaurant.objects.annotate(
            avg_rating = Avg('reviews__rating'),
            reviews_count=Count('reviews')
            )
        
        query_value = self.request.GET.get('q')
        query_top = self.request.GET.get('top')
        if query_value:
            queryset = queryset.filter(
                Q(name__icontains=query_value) | 
                Q(address__icontains = query_value) | 
                Q(description__icontains = query_value
                ))
        if query_top:
            queryset = queryset.filter(avg_rating__gte = 4.5)
        return queryset

class BaseView(View):
    def get(self, request):
        return render(request, 'base.html')



class RestaurantDetailView(LoginRequiredMixin, DetailView):
    template_name = "reviews/restaurant.html"
    model = Restaurant
    context_object_name = "restaurant"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ReviewForm()
        context["allreviews"] = self.object.reviews.all
        return context
    def post(self, request, *args, **kwargs):
        restaurant = self.get_object()
        self.object = restaurant
        form = ReviewForm(request.POST, request.FILES)
        already_exists = Review.objects.filter(restaurant=restaurant, user=request.user).exists()
        if already_exists:
            messages.warning(request, "Ви вже залишили відгук для цього закладу. Дякуємо!")
            return redirect('restaurant-detail', pk=restaurant.pk)
        if form.is_valid():
            review = form.save(commit=False)
            review.restaurant = restaurant
            review.user = request.user
            review.save()
            return redirect('restaurant-detail', pk=restaurant.pk)
        context = self.get_context_data(object = restaurant)
        context["form"] = form
        return self.render_to_response(context)

class LoginUserView(LoginView):
    authentication_form = LoginForm
    template_name = 'registration/login.html'

class LogoutUserView(LogoutView):
    next_page = 'restaurants'

class SignUpView(CreateView):
    template_name = "registration/signup.html"
    form_class = UserCreationForm
    success_url = reverse_lazy('login')

class ProfileView(TemplateView):
    template_name = "registration/profile.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reviews"] = Review.objects.filter(user = self.request.user)
        return context

def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    if request.method == 'POST':
        review.delete()
        return redirect('profile')
    return redirect('profile')

def update_review(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('profile')
    return redirect('profile')


