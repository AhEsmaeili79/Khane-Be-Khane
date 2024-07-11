from django.contrib import admin
from .models import User, House, Order, Review

admin.site.register(User)
admin.site.register(House)
admin.site.register(Order)
admin.site.register(Review)