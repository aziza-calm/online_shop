from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (Courier, Order, WorkingHours, DeliveryHours)
from .views import (post_orders, post_couriers, assign, complete, courier)


class ViewTest(TestCase):
    def setUp(self):
        self.couriers = []
        courier = Courier(
            external_id=1,
            type=Courier.foot,
            regions=[1, 2, 3]
        )
        courier.save()
        self.couriers.append(courier)
        working_hours = WorkingHours(
            start_timestamp=580,
            finish_timestamp=1080,
            courier=courier
        )
        working_hours.save()

        courier = Courier(
            external_id=2,
            type=Courier.bike,
            regions=[2, 3]
        )
        courier.save()
        self.couriers.append(courier)
        working_hours = WorkingHours(
            start_timestamp=580,
            finish_timestamp=1080,
            courier=courier
        )
        working_hours.save()

        courier = Courier(
            external_id=3,
            type=Courier.car,
            regions=[1, 2, 3],
            assign_time=timezone.now()
        )
        courier.save()
        self.couriers.append(courier)
        working_hours = WorkingHours(
            start_timestamp=580,
            finish_timestamp=660,
            courier=courier
        )
        working_hours.save()
        working_hours = WorkingHours(
            start_timestamp=700,
            finish_timestamp=990,
            courier=courier
        )
        working_hours.save()

        self.orders = []
        order = Order(
            external_id=1,
            weight=45,
            region=3,
            assignee=self.couriers[2],
            payment=self.couriers[2].get_payment()
        )
        order.save()
        self.orders.append(order)
        delivery_hours = DeliveryHours(
            start_timestamp=650,
            finish_timestamp=750,
            order=order
        )
        delivery_hours.save()

        order = Order(
            external_id=2,
            weight=1,
            region=2
        )
        order.save()
        self.orders.append(order)
        delivery_hours = DeliveryHours(
            start_timestamp=900,
            finish_timestamp=1200,
            order=order
        )
        delivery_hours.save()

        order = Order(
            external_id=3,
            weight=10,
            region=2
        )
        order.save()
        self.orders.append(order)
        delivery_hours = DeliveryHours(
            start_timestamp=0,
            finish_timestamp=800,
            order=order
        )
        delivery_hours.save()

    def test_create_couriers(self):
        resp = self.client.post(reverse('restful:post_couriers'), {
            "data": [
                {
                    "courier_id": 4,
                    "courier_type": "foot",
                    "regions": [1, 12, 22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                },
                {
                    "courier_id": 5,
                    "courier_type": "bike",
                    "regions": [2],
                    "working_hours": ["09:00-18:00"]
                },
                {
                    "courier_id": 6,
                    "courier_type": "car",
                    "regions": [1, 2, 3, 33],
                    "working_hours": []
                }
            ]
        }, content_type='application/json')
        self.assertEqual(resp.status_code, 201)

    def test_create_orders(self):
        resp = self.client.post(reverse('restful:post_orders'), {
            "data": [
                {
                    "order_id": 4,
                    "weight": 0.23,
                    "region": 12,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 5,
                    "weight": 15,
                    "region": 1,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 6,
                    "weight": 0.01,
                    "region": 22,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                }
            ]
        }, content_type='application/json')
        self.assertEqual(resp.status_code, 201)

    def test_get_courier(self):
        resp = self.client.get(reverse('restful:courier', kwargs={'external_id': 2}))
        self.assertEqual(resp.status_code, 200)

    def test_patch_courier(self):
        resp = self.client.patch(reverse('restful:courier', kwargs={'external_id': 2}), {
            "courier_type": "bike",
            "regions": [],
            "working_hours": []
        }, content_type='application/json')
        self.assertEqual(resp.status_code, 200)

    def test_assign(self):
        resp = self.client.post(reverse('restful:assign'),
                                {
                                    "courier_id": 1
                                }, content_type='application/json')
        self.assertEqual(resp.status_code, 200)

    def test_complete(self):
        resp = self.client.post(reverse('restful:complete'),
                                {
                                    "courier_id": 3,
                                    "order_id": 1,
                                    "complete_time": "2022-05-10T10:33:01.42Z"
                                }
                                , content_type='application/json')
        self.assertEqual(resp.status_code, 200)
