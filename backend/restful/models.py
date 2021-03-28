from django.contrib.postgres.fields import ArrayField
from django.db import models


class Hours(models.Model):
    start_timestamp = models.IntegerField(blank=False)
    finish_timestamp = models.IntegerField(blank=False)

    @staticmethod
    def get_timestamp(obj):
        if isinstance(obj, str):
            return int(obj.split(':')[0]) * 60 + int(obj.split(':')[1])
        #elif isinstance(obj, )
        else:
            raise NotImplementedError("Can't parse {} to timestamp".format(str(obj)))

    def get_string(self):
        return "{:02d}:{:02d}-{:02d}:{:02d}".format(
            self.start_timestamp // 60,
            self.start_timestamp % 60,
            self.finish_timestamp // 60,
            self.finish_timestamp % 60
        )

    class Meta:
        abstract = True


class Courier(models.Model):
    FOOT = 'FOOT'
    BIKE = 'BIKE'
    CAR = 'CAR'
    TYPE_CHOICES = (
        (FOOT, "Пеший"),
        (BIKE, "Велокурьер"),
        (CAR, "Курьер на автомобиле")
    )

    external_id = models.IntegerField(blank=False, db_index=True)
    type = models.CharField(
        max_length=100, choices=TYPE_CHOICES, blank=False
    )
    regions = ArrayField(models.IntegerField(), blank=False)

    carrying_map = {
        FOOT: 10,
        BIKE: 15,
        CAR: 50,
    }

    def get_carrying(self):
        return self.carrying_map[self.type]


class WorkingHours(Hours):
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE, blank=False, related_name='working_hours')


class Order(models.Model):
    external_id = models.IntegerField(blank=False, db_index=True)
    weight = models.FloatField(blank=False)
    region = models.IntegerField(blank=False)


class DeliveryHours(Hours):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=False, related_name='delivery_hours')
