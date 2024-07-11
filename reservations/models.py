from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from PIL import Image

class User(AbstractUser):
    ROLES = (
        (1, 'Admin'),
        (2, 'Host'),
        (3, 'Passenger'),
    )
    role = models.IntegerField(choices=ROLES, default=3)
    phonenumber = models.CharField(max_length=15)
    address = models.TextField()
    role_change_requested = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

class House(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='house_images/')
    city = models.CharField(max_length=100)
    number_of_rooms = models.IntegerField()
    area = models.FloatField()
    number_of_parkings = models.IntegerField()
    capacity = models.IntegerField()
    price_per_day = models.IntegerField()
    pool = models.BooleanField(default=False)
    oven = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img_path = self.image.path
            img = Image.open(img_path)
            img = img.resize((1000, 1000), Image.LANCZOS)
            img.save(img_path)

class Order(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    arrive_date = models.DateField()
    exit_date = models.DateField()
    count_of_passengers = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

class Review(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=((1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')))
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('house', 'user')

    def __str__(self):
        return f'Review by {self.user.username} on {self.house.name}'