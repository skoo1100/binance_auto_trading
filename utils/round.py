from decimal import Decimal

# 소수점 자릿수 맞추기
def round_value(value, step):
    """
    value (float): 자릿수 맞출 숫자
    step (str 또는 float): ex. '0.001'
    """
    step_decimal = Decimal(str(step))
    value_decimal = Decimal(str(value))
    rounded = (value_decimal // step_decimal) * step_decimal
    str_step = format(step_decimal.normalize(), 'f')
    decimal_places = len(str_step.split('.')[1]) if '.' in str_step else 0
    return format(rounded, f'.{decimal_places}f')