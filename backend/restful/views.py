from django.http import JsonResponse
from .models import (
    Hours, Courier, Order, WorkingHours, DeliveryHours
)
from django.views.decorators.csrf import csrf_exempt
import json
from .utils import method_check, validate_dict


@csrf_exempt
@method_check(['POST'])
def post_courier(request):
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
            })
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
