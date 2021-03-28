from django.urls import path
from .views import post_couriers, courier, post_orders


app_name = "restful"
# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('couriers', post_couriers, name='post_couriers'),
    path('couriers/<int:external_id>', courier, name='courier'),
    path('orders', post_orders, name='post_orders'),
]