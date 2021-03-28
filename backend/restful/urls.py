from django.urls import path
from .views import post_courier


app_name = "restful"
# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('couriers', post_courier, name='post_courier'),
    #path('couriers/<int:pk>', CourierView.as_view())
]