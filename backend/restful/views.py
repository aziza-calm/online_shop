from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, Min, Sum
import json
import dateutil.parser
from .models import (
    Hours, Courier, Order, WorkingHours, DeliveryHours
)
from .utils import method_check, validate_dict


@csrf_exempt
@method_check(['POST'])
def post_couriers(request):
    try:
        body = json.loads(request.body.decode())
    except (json.decoder.JSONDecodeError, ValueError):
        return JsonResponse({
            'error': 'Unable to parse request body',
        }, status=400)

    if 'data' in body and isinstance(body['data'], list):
        wrong_couries = []
        for item in body['data']:
            errors = validate_dict(item, {
                'courier_id': int,
                'courier_type': str,
                'regions': list,
                'working_hours': list,
            }, {}, {})
            if len(errors) > 0:
                if 'courier_id' in item:
                    errors['id'] = item['courier_id']
                wrong_couries.append(errors)
        if len(wrong_couries) > 0:
            return JsonResponse({
                'validation_error': {
                    'couriers': wrong_couries
                },
            }, status=400)
    else:
        return JsonResponse({
            'error': 'No valid data key presented',
        }, status=400)

    couriers_to_create = []
    for item in body['data']:
        couriers_to_create.append(
            Courier(
                external_id=item['courier_id'],
                type=item['courier_type'],
                regions=item['regions'],
            )
        )
    created_couriers = Courier.objects.bulk_create(couriers_to_create)

    whours_to_create = []
    for item, courier in zip(body['data'], created_couriers):
        for whours in item['working_hours']:
            whours_to_create.append(
                WorkingHours(
                    start_timestamp=Hours.get_timestamp(whours.split('-')[0]),
                    finish_timestamp=Hours.get_timestamp(whours.split('-')[1]),
                    courier=courier
                )
            )
    created_whours = WorkingHours.objects.bulk_create(whours_to_create)

    return JsonResponse({
        'couriers': [{'id': created_courier.external_id} for created_courier in created_couriers],
    }, status=201)


@csrf_exempt
@method_check(['GET', 'PATCH'])
def courier(request, external_id):
    try:
        courier = Courier.objects.get(external_id=external_id)
    except Courier.DoesNotExist:
        return JsonResponse({
            'error': 'Courier with id {} does not exist'.format(external_id),
        }, status=400)
    if request.method == 'GET':
        response = courier.get_dict()
        finished = Order.objects.filter(
            assignee=courier, delivery_time__isnull=False
        )
        min_avg_time = finished.annotate(
            avg_time=Avg('delivery_time')
        ).aggregate(Min('avg_time'))['avg_time__min']
        if min_avg_time and min_avg_time > 0:
            response['rating'] = (60*60 - min(min_avg_time, 60*60))/(60*60) * 5
        earnings = finished.aggregate(earnings=Sum('payment'))['earnings']
        if earnings:
            response['earnings'] = earnings
        else:
            response['earnings'] = 0
        return JsonResponse(response, status=200)
    else:
        try:
            body = json.loads(request.body.decode())
        except (json.decoder.JSONDecodeError, ValueError):
            return JsonResponse({
                'error': 'Unable to parse request body',
            }, status=400)

    errors = validate_dict(body, {}, {
        'courier_type': str,
        'regions': list,
        'working_hours': list,
    }, {
        'courier_type': lambda type: None if type in [x[0] for x in Courier.TYPE_CHOICES] else 'Invalid courier type'
    })
    if len(errors) > 0:
        return JsonResponse({
            'validation_error': errors,
        }, status=400)

    if 'courier_type' in body:
        courier.type = body['courier_type']
        courier.save()
        for order in Order.objects.filter(
                assignee=courier, delivery_time__isnull=True, weight__gt=courier.get_carrying()
        ):
            order.assignee = None
            order.payment = None
            order.save()
    if 'regions' in body:
        courier.regions = body['regions']
        courier.save()
        for order in Order.objects.filter(
                assignee=courier, delivery_time__isnull=True
        ).exclude(region__in=courier.regions):
            order.assignee = None
            order.payment = None
            order.save()

    if 'working_hours' in body:
        courier.working_hours.all().delete()
        whours_to_create = []
        for whours in body['working_hours']:
            whours_to_create.append(
                WorkingHours(
                    start_timestamp=Hours.get_timestamp(whours.split('-')[0]),
                    finish_timestamp=Hours.get_timestamp(whours.split('-')[1]),
                    courier=courier
                )
            )
        created_whours = WorkingHours.objects.bulk_create(whours_to_create)
        for order in Order.objects.filter(
                assignee=courier, delivery_time__isnull=True
        ):
            order_saved = False
            for dhours in order.delivery_hours:
                for whours in created_whours:
                    if (
                            (whours.start_timestamp < dhours.start_timestamp < whours.finish_timestamp) or
                            (whours.start_timestamp < dhours.finish_timestamp < whours.finish_timestamp)
                    ):
                        order_saved = True
                        break
                if order_saved:
                    break
            if not order_saved:
                order.assignee = None
                order.payment = None
                order.save()

    return JsonResponse(courier.get_dict(), status=200)


@csrf_exempt
@method_check(['POST'])
def post_orders(request):
    try:
        body = json.loads(request.body.decode())
    except (json.decoder.JSONDecodeError, ValueError):
        return JsonResponse({
            'error': 'Unable to parse request body',
        }, status=400)

    if 'data' in body and isinstance(body['data'], list):
        wrong_orders = []
        for item in body['data']:
            errors = validate_dict(item, {
                'order_id': int,
                'weight': (int, float),
                'region': int,
                'delivery_hours': list,
            }, {}, {
                'weight': lambda w: None if 0.01 <= w <= 50 else 'Incorrect weight'
            })
            if len(errors) > 0:
                if 'order_id' in item:
                    errors['id'] = item['order_id']
                wrong_orders.append(errors)
        if len(wrong_orders) > 0:
            return JsonResponse({
                'validation_error': {
                    'orders': wrong_orders
                },
            }, status=400)
    else:
        return JsonResponse({
            'error': 'No valid data key presented',
        }, status=400)

    orders_to_create = []
    for item in body['data']:
        orders_to_create.append(
            Order(
                external_id=item['order_id'],
                weight=item['weight'],
                region=item['region'],
            )
        )
    created_orders = Order.objects.bulk_create(orders_to_create)

    dhours_to_create = []
    for item, order in zip(body['data'], created_orders):
        for dhours in item['delivery_hours']:
            dhours_to_create.append(
                DeliveryHours(
                    start_timestamp=Hours.get_timestamp(dhours.split('-')[0]),
                    finish_timestamp=Hours.get_timestamp(dhours.split('-')[1]),
                    order=order
                )
            )
    created_dhours = DeliveryHours.objects.bulk_create(dhours_to_create)

    return JsonResponse({
        'orders': [{'id': created_order.external_id} for created_order in created_orders],
    }, status=201)


@csrf_exempt
@method_check(['POST'])
def assign(request):
    try:
        body = json.loads(request.body.decode())
    except (json.decoder.JSONDecodeError, ValueError):
        return JsonResponse({
            'error': 'Unable to parse request body',
        }, status=400)

    try:
        courier = Courier.objects.get(external_id=body['courier_id'])
    except Courier.DoesNotExist:
        return JsonResponse({
            'error': 'Courier with id {} does not exist'.format(body['courier_id']),
        }, status=400)

    filtered_orders = Order.objects.filter(
        weight__lte=courier.get_carrying(),
        region__in=courier.regions,
        assignee__isnull=True
    )

    order_ids = []
    for working_hour in courier.working_hours.all():
        order_ids.extend(list(DeliveryHours.objects.filter(
            order__in=filtered_orders,
            start_timestamp__lte=working_hour.start_timestamp,
            finish_timestamp__gte=working_hour.start_timestamp
        ).values_list('order__id', flat=True)))
        order_ids.extend(list(DeliveryHours.objects.filter(
            order__in=filtered_orders,
            start_timestamp__lte=working_hour.finish_timestamp,
            finish_timestamp__gte=working_hour.finish_timestamp
        ).values_list('order__id', flat=True)))

    acceptable_orders = Order.objects.filter(id__in=set(order_ids))

    assign_time = timezone.now()
    payment = courier.get_payment()
    for order in acceptable_orders:
        order.assignee = courier
        order.payment = payment
        order.save()

    response = {
        'orders': [{'id': order.external_id} for order in acceptable_orders]
    }

    if len(acceptable_orders) > 0:
        courier.assign_time = assign_time
        courier.save()
        response['assign_time'] = assign_time.isoformat("T")

    return JsonResponse(response, status=200)


@csrf_exempt
@method_check(['POST'])
def complete(request):
    try:
        body = json.loads(request.body.decode())
    except (json.decoder.JSONDecodeError, ValueError):
        return JsonResponse({
            'error': 'Unable to parse request body',
        }, status=400)

    try:
        courier = Courier.objects.get(external_id=body['courier_id'])
    except Courier.DoesNotExist:
        return JsonResponse({
            'error': 'Courier with id {} does not exist'.format(body['courier_id']),
        }, status=400)

    try:
        order = Order.objects.get(external_id=body['order_id'])
    except Courier.DoesNotExist:
        return JsonResponse({
            'error': 'Order with id {} does not exist'.format(body['courier_id']),
        }, status=400)

    if order.assignee != courier:
        return JsonResponse({
            'error': 'Order {} is not assigned to courier {}'.format(
                body['order_id'], body['courier_id']),
        }, status=400)

    complete_time = dateutil.parser.isoparse(body['complete_time'])
    if courier.complete_time:
        start_time = courier.complete_time
    else:
        start_time = courier.assign_time
    courier.complete_time = complete_time
    courier.save()
    order.delivery_time = (complete_time-start_time).total_seconds()
    order.save()

    return JsonResponse({'order_id': order.external_id}, status=200)






