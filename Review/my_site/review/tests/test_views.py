from django.test import TestCase
from ..models import Restaurant, Review, Profile
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile

class RestaurantListViewTests(TestCase):
    def setUp(self):
        self.r1 = Restaurant.objects.create(name="Pizza Hut", address="Kyiv")
        self.r2 = Restaurant.objects.create(name="Sushi Master", address="Lviv")
        
    def test_base_view(self):
        response = self.client.get(reverse('review-home'))
        self.assertEqual(response.status_code, 200)
    
    def test_restaurant_list_no_filter(self):
        response = self.client.get(reverse('restaurants')) 
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pizza Hut')
        self.assertContains(response, 'Sushi Master')

    def test_restaurant_search(self):
        response = self.client.get(reverse('restaurants'), {'q':'Pizza'})
        self.assertContains(response, 'Pizza Hut')
        self.assertNotContains(response, 'Sushi Master')

    def test_restaurant_top(self):
        user = User.objects.create(username='Testuser')
        Review.objects.create(restaurant=self.r1, user=user, rating=5, text='Top')
        response = self.client.get(reverse('restaurants'), {'top':'true'})
        self.assertContains(response, 'Pizza Hut')
        self.assertNotContains(response, 'Sushi Master')


class RestaurantDetailViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="vitaliy", password="123")
        self.restaurant = Restaurant.objects.create(name="Пузата Хата", address="Київ")
        self.url = reverse('restaurant-detail', kwargs={'pk': self.restaurant.pk})

    def test_get_context_data(self):
        self.client.login(username="vitaliy", password='123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context) 
        self.assertIn('allreviews', response.context)
    
    def test_post_review_already_exists(self):
        self.client.login(username='vitaliy', password='123')
        Review.objects.create(restaurant=self.restaurant, user=self.user, rating=5, text="Один")
        response = self.client.post(self.url, {'rating':'4', 'text': 'Другий'})
        self.assertRedirects(response, self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Ви вже залишили відгук для цього закладу. Дякуємо!")

    def test_post_review_success(self):
        self.client.login(username="vitaliy", password="123")
        data = {
            'rating': 5,
            'text': 'Неймовірно смачно'
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, self.url)
        self.assertTrue(Review.objects.filter(text='Неймовірно смачно').exists())

    def test_post_review_invalid(self):
        self.client.login(username="vitaliy", password="123")
        response = self.client.post(self.url, {'rating': '', 'text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())

class ProfileUpdateViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="vitaliy", password='123')
        self.profile, _ = Profile.objects.get_or_create(user=self.user)
        self.client.login(username='vitaliy', password='123')
        self.url = reverse('profile')
    def test_profile_update_get(self):
        restaurant = Restaurant.objects.create(name='Testrestaurnat')
        Review.objects.create(restaurant=restaurant, user=self.user, rating=5, text="Мій відгук")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object'], self.profile)
        self.assertEqual(response.context['reviews'].count(), 1)
        self.assertEqual(response.context['reviews'][0].restaurant.name, "Testrestaurnat")

    def test_profile_update_post_valid(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        avatar = SimpleUploadedFile("test_avatar.gif", small_gif, content_type="image/gif")
        data = {
            'bio': 'Оновлена біографія через UpdateView',
            'avatar': avatar
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('profile'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Профіль успішно оновлено!")

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, 'Оновлена біографія через UpdateView')


class ReviewDeleteViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="deleter", password="123")
        self.restaurant = Restaurant.objects.create(name="Кафе")
        self.review = Review.objects.create(restaurant=self.restaurant, user=self.user, rating=4, text="Видали мене")
        self.client.login(username="deleter", password="123")
        self.url = reverse('delete_review', kwargs={'pk': self.review.pk})

    def test_delete_review_success(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('profile'))
        self.assertFalse(Review.objects.filter(pk=self.review.pk).exists())

class ReviewUpdateViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="editor", password="123")
        self.restaurant = Restaurant.objects.create(name="Ресторан")
        self.review = Review.objects.create(restaurant=self.restaurant, user=self.user, rating=3, text="Старий текст")
        self.client.login(username="editor", password="123")
        self.url = reverse('update_review', kwargs={'pk': self.review.pk})

    def test_update_review_post_valid(self):
        data = {'rating': 5, 'text': 'Новий текст'}
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('profile'))
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.text, 'Новий текст')

    def test_update_review_post_invalid(self):
        response = self.client.post(self.url, {'rating': 10, 'text': ''})
        self.assertRedirects(response, reverse('profile'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Помилка" in m.message for m in messages))