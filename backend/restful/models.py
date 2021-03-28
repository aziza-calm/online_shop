from django.contrib.postgres.fields import ArrayField
from django.db import models


class Hours(models.Model):
    start_timestamp = models.IntegerField(blank=False)
    finish_timestamp = models.IntegerField(blank=False)

    @staticmethod
    def get_timestamp(obj):
        if isinstance(obj, str):
            return int(obj.split(':')[0]) * 60 + int(obj.split(':')[1])
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
    foot = 'foot'
    bike = 'bike'
    car = 'car'
    TYPE_CHOICES = (
        (foot, "Пеший"),
        (bike, "Велокурьер"),
        (car, "Курьер на автомобиле")
    )

    external_id = models.IntegerField(blank=False, db_index=True)
    type = models.CharField(
        max_length=100, choices=TYPE_CHOICES, blank=False
    )
    regions = ArrayField(models.IntegerField(), blank=False)
    assign_time = models.DateTimeField(blank=True, null=True)
    complete_time = models.DateTimeField(blank=True, null=True)

    carrying_map = {
        foot: 10,
        bike: 15,
        car: 50,
    }

    payment_map = {
        foot: 2,
        bike: 5,
        car: 9,
    }

    def get_carrying(self):
        return self.carrying_map[self.type]

    def get_payment(self):
        return 500 * self.payment_map[self.type]

    def get_dict(self):
        return {
            'courier_id': self.external_id,
            'courier_type': self.type,
            'regions': self.regions,
            'working_hours': [whours.get_string() for whours in self.working_hours.all()]
        }


class WorkingHours(Hours):
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE, blank=False, related_name='working_hours')


class Order(models.Model):
    external_id = models.IntegerField(blank=False, db_index=True)
    weight = models.FloatField(blank=False)
    region = models.IntegerField(blank=False)
    assignee = models.ForeignKey(
        Courier, on_delete=models.CASCADE, blank=True, null=True, related_name='assigned_orders'
    )
    payment = models.IntegerField(blank=True, null=True)
    delivery_time = models.IntegerField(blank=True, null=True)


class DeliveryHours(Hours):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=False, related_name='delivery_hours')
