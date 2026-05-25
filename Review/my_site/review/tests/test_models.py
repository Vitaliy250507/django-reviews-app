from django.test import TestCase
from ..models import Restaurant, Review, Profile
from django.contrib.auth.models import User

class TestAppModels(TestCase):

    def test_profile_str(self):
        user = User.objects.create(username="Testusername")
        profile, created = Profile.objects.get_or_create(user=user)
        self.assertEqual(str(profile), f"Профіль: {user.username}")
    
    def test_review_str(self):
        user = User.objects.create(username="Testusername")
        restaurant = Restaurant.objects.create(name="Пузата Хата")
        review, created = Review.objects.get_or_create(user=user, restaurant=restaurant, rating=5, text="Дуже смачно")
        expected_str = f"Відгук від {user.username} для {restaurant.name}"
        self.assertEqual(str(review), expected_str)

    def test_restaurant_get_avg_rating_no_reviews(self):
        restaurant = Restaurant.objects.create(name="Testrestaurant")
        self.assertEqual(restaurant.get_avg_rating(), 0)

    def test_restaurant_get_avg_rating_with_reviews(self):
        restaurant = Restaurant.objects.create(name="Testrestaurant")
        user1 = User.objects.create(username="Critic1")
        Review.objects.create(restaurant=restaurant, user=user1, rating=3, text="Ну норм")
        user2 = User.objects.create(username="Critic2")
        Review.objects.create(restaurant=restaurant, user=user2, rating=5, text="Супер")
        self.assertEqual(restaurant.get_avg_rating(), 4.0)

    def test_restaurant_str(self):
        restaurant = Restaurant.objects.create(name="Testname")
        self.assertEqual(str(restaurant), restaurant.name)

