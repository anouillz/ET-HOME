import random

from django import template

register = template.Library()

nums = "0123456789"
alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

@register.simple_tag
def rand_alphanum(length):
    return "".join(random.sample(alpha + nums, length))

@register.simple_tag
def rand_int(a, b=None):
    if b is None:
        a, b = 0, a
    return random.randint(a, b)

@register.simple_tag
def rand_float(a, b=None, max_decimals=None):
    if b is None:
        a, b = 0, a
    value = random.random() * (b - a) + a
    if max_decimals is not None:
        value = str(value)
        integer, decimal = value.split(".")
        decimal = decimal[:max_decimals]
        value = float(integer + "." + decimal)
    return value

@register.simple_tag
def rand_choice(choices):
    return random.choice(choices)
