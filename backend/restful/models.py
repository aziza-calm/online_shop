from django.contrib.postgres.fields import ArrayField
from django.db import models


class Courier(models.Model):
    FOOT = 'FOOT'
    BIKE = 'BIKE'
    CAR = 'CAR'
    TYPE_CHOICES = (
        (FOOT, "Пеший"),
        (BIKE, "Велокурьер"),
        (CAR, "Курьер на автомобиле")
    )

    type = models.CharField(
        max_length=100, choices=TYPE_CHOICES, blank=False
    )
    regions = ArrayField(models.IntegerField(), blank=False)


class WorkingHours(models.Model):
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE, blank=False, related_name='working_hours')
    start_timestamp = models.IntegerField(blank=False)
    finish_timestamp = models.IntegerField(blank=False)


class Order(models.Model):
    weight = models.FloatField(blank=False)
    region = models.IntegerField(blank=False)


class DeliveryHours(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=False, related_name='delivery_hours')
    start_timestamp = models.IntegerField(blank=False)
    finish_timestamp = models.IntegerField(blank=False)
