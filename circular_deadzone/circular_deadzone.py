import math

import gremlin
from gremlin.user_plugin import *


mode = ModeVariable("Mode", "Mode in which to use these settings")

pa_x = PhysicalInputVariable(
        "Physical X Axis",
        "Physical X axis input",
        [gremlin.common.InputType.JoystickAxis]
)
pa_y = PhysicalInputVariable(
        "Physical Y Axis",
        "Physical Y axis input",
        [gremlin.common.InputType.JoystickAxis]
)
va_x = VirtualInputVariable(
        "vJoy X Axis",
        "Virtual X axis output",
        [gremlin.common.InputType.JoystickAxis]
)
va_y = VirtualInputVariable(
        "vJoy Y Axis",
        "Virtual Y axis output",
        [gremlin.common.InputType.JoystickAxis]
)
inner_dz = FloatVariable(
        "Inner Deadzone",
        "Size of the inner deadzone",
        0.0,
        0.0,
        1.0
)
outer_dz = FloatVariable(
        "Outer Deadzone",
        "Size of the outer deadzone",
        1.0,
        0.0,
        1.0
)


# Decorators for the two physical axes
dec_x = pa_x.create_decorator(mode.value)
dec_y = pa_y.create_decorator(mode.value)


# Storage for the last known axis values
x_value = 0.0
y_value = 0.0


class Vector2:

    def __init__(self, x, y):
        self.x = x
        self.y = y


def update_vjoy(vjoy):
    alpha = math.atan2(y_value, x_value)
    
    lower = Vector2(
        abs(math.cos(alpha) * inner_dz.value),
        abs(math.sin(alpha) * inner_dz.value)
    )
    upper = Vector2(outer_dz.value, outer_dz.value)

    px = max(0.0, min(1.0, (abs(x_value) - lower.x) / (upper.x - lower.x)))
    py = max(0.0, min(1.0, (abs(y_value) - lower.y) / (upper.y - lower.y)))

    vjoy[va_x.vjoy_id].axis(va_x.input_id).value = math.copysign(px, x_value)
    vjoy[va_y.vjoy_id].axis(va_y.input_id).value = math.copysign(py, y_value)


@dec_x.axis(pa_x.input_id)
def axis1(event, vjoy):
    global x_value
    x_value = event.value
    update_vjoy(vjoy)


@dec_y.axis(pa_y.input_id)
def axis2(event, vjoy):
    global y_value
    y_value = event.value
    update_vjoy(vjoy)

