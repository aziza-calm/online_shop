from django.http import JsonResponse


def method_check(expected_methods):
    def method_check_decorator(function):
        def wrapper(request, *args, **kwargs):
            if request.method in expected_methods:
                return function(request, *args, **kwargs)
            else:
                return JsonResponse({
                    'method_error': 'Invalid request method {}, expected one of {}'.format(request.method, str(expected_methods)),
                }, status=405)
        return wrapper
    return method_check_decorator


def validate_dict(obj, to_check):
    errors = {}
    for field_name, field_value in obj.items():
        if field_name in to_check:
            if not isinstance(field_value, to_check[field_name]):
                errors[field_name] = 'Unexpected field type {}, expected {}'.format(
                    type(field_value), to_check[field_name]
                )
        else:
            errors[field_name] = 'Unexpected field'
    for expected_field, expected_type in to_check.items():
        if expected_field not in obj:
            errors[expected_field] = 'Missing field'

    return errors
