from django.http import JsonResponse
from .models import (
    Hours, Courier, Order, WorkingHours, DeliveryHours
)
from django.views.decorators.csrf import csrf_exempt
import json
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
                type=item['courier_type'].upper(),
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
        }, status=404)
    if request.method == 'GET':
        return JsonResponse(courier.get_dict(), status=200)
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
    })
    if len(errors) > 0:
        return JsonResponse({
            'validation_error': errors,
        }, status=400)

    if 'courier_type' in body:
        courier.type = body['courier_type'].upper()
    if 'regions' in body:
        courier.regions = body['regions']
    courier.save()

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

    # TODO: логика проверки имеющихся заказов

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
                'weight': lambda w: None if w >= 0.01 and w <= 50 else 'Incorrect weight'
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
