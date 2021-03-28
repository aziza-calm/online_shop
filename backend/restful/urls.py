from django.urls import path
from .views import CourierView


app_name = "articles"
# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('couriers/', CourierView.as_view()),
    path('couriers/<int:pk>', CourierView.as_view())
]