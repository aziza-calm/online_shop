from django.http import JsonResponse
import json


def method_check(expected_methods):
    def method_check_decorator(function):
        def wrapper(request, *args, **kwargs):
            if request.method in expected_methods:
                return function(request, *args, **kwargs)
            else:
                return JsonResponse({
                    'error': 'Invalid request method {}, expected one of {}'.format(request.method, str(expected_methods)),
                }, status=405)
        return wrapper
    return method_check_decorator


def validate_dict(obj, expected, possible, rules):
    errors = {}
    for field_name, field_value in obj.items():
        if field_name in expected:
            if not isinstance(field_value, expected[field_name]):
                errors[field_name] = 'Unexpected field type {}, expected {}'.format(
                    type(field_value), expected[field_name]
                )
        elif field_name in possible:
            if not isinstance(field_value, possible[field_name]):
                errors[field_name] = 'Unexpected field type {}, expected {}'.format(
                    type(field_value), possible[field_name]
                )
        else:
            errors[field_name] = 'Unexpected field'
        if field_name in rules and field_name not in errors:
            rule_output = rules[field_name](field_value)
            if rule_output:
                errors[field_name] = rule_output
    for expected_field, expected_type in expected.items():
        if expected_field not in obj:
            errors[expected_field] = 'Missing field'

    return errors
