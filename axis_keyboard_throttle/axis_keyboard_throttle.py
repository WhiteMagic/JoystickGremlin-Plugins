import math
import time
import gremlin
from gremlin.user_plugin import *


mode = ModeVariable("Mode", "The mode in which to use this mapping")

axis = PhysicalInputVariable(
        "Input axis",
        "Axis to treat as throttle input",
        [gremlin.common.InputType.JoystickAxis]
)

inc_out = StringVariable(
        "Increment throttle",
        "Key pressed to increment the throttle",
        "2"
)

dec_out = StringVariable(
        "Reduce throttle",
        "Key pressed to reduce the throttle",
        "1"
)

step_size = FloatVariable(
        "Step size",
        "Amount of change per step",
        0.05,
        0.0,
        1.0
)

# Decorators for the two physical axes
decorator = axis.create_decorator(mode.value)

# Storage for axis values
g_last_value = 0.0

# Increment macro
inc_macro = gremlin.macro.Macro()
inc_macro.exclusive = True
inc_macro.tap(inc_out.value)
inc_macro.repeat = gremlin.macro.CountRepeat(1, 0.01)

# Decrement macro
dec_macro = gremlin.macro.Macro()
dec_macro.exclusive = True
dec_macro.tap(dec_out.value)
dec_macro.repeat = gremlin.macro.CountRepeat(1, 0.01)

# Handle to the macro manager
macro_manager = gremlin.macro.MacroManager()


@decorator.axis(axis.input_id)
def throttle_to_keyboard(event, vjoy):
    """Sets the throttle to the desired value ensuring a consistent amount
    of key presses are sent, i.e. one per 5% of change in an axis.
    """
    global g_last_value
    cur_value = event.value

    delta = cur_value - g_last_value
    count = math.floor(abs(delta) / step_size.value)
    action = inc_macro if delta > 0 else dec_macro

    if count > 0:
        g_last_value = cur_value
        action.repeat.count = count
        macro_manager.queue_macro(action)

