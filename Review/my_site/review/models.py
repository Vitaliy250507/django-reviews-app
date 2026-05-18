from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

# Create your models here.

class Restaurant(models.Model):
    name = models.CharField("Назва закладу:", max_length=100)
    description = models.TextField("Опис:")
    address = models.CharField("Адреса:", max_length=100)
    image = models.ImageField("Фото закладу", upload_to='restaurants/')
    created_at = models.DateField(auto_now_add = True)

    def get_avg_rating(self):
        sum = 0
        reviews = self.reviews.all()
        count = reviews.count()
        
        if count == 0:
            return 0
        for review in reviews:
            sum += review.rating
        return round(sum / reviews.count(), 1)

    
    def __str__(self):
        return self.name
    
    
class Review(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField("Рейтинг (1-5):", validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField("Ваш відгук")
    food_img = models.ImageField("Фото страви", upload_to="reviews/", null=True, blank=True)
    created_at = models.DateField(auto_now_add = True)

    class Meta:
        unique_together = ("restaurant", "user")

    def __str__(self):
        return f"Відгук від {self.user.username} для {self.restaurant.name}"