import time
import gremlin
from gremlin.user_plugin import *


mode = ModeVariable("Mode", "The mode in which to use this mapping")

axis = PhysicalInputVariable(
        "Input axis",
        "Input axis",
        [gremlin.common.InputType.JoystickAxis]
)

inc_out = VirtualInputVariable(
        "Increment output button",
        "Increment output button",
        [gremlin.common.InputType.JoystickButton]
)

dec_out = VirtualInputVariable(
        "Decrement output button",
        "Decrement output button",
        [gremlin.common.InputType.JoystickButton]
)

step_size = FloatVariable(
        "Amount of change per step",
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
inc_macro.add_action(gremlin.macro.VJoyAction(
    inc_out.vjoy_id,
    gremlin.common.InputType.JoystickButton,
    inc_out.input_id,
    True
))
inc_macro.add_action(gremlin.macro.PauseAction(0.05))
inc_macro.add_action(gremlin.macro.VJoyAction(
    inc_out.vjoy_id,
    gremlin.common.InputType.JoystickButton,
    inc_out.input_id,
    False
))

# Decrement macro
dec_macro = gremlin.macro.Macro()
dec_macro.exclusive = True
dec_macro.add_action(gremlin.macro.VJoyAction(
    dec_out.vjoy_id,
    gremlin.common.InputType.JoystickButton,
    dec_out.input_id,
    True
))
dec_macro.add_action(gremlin.macro.PauseAction(0.05))
dec_macro.add_action(gremlin.macro.VJoyAction(
    dec_out.vjoy_id,
    gremlin.common.InputType.JoystickButton,
    dec_out.input_id,
    False
))


@decorator.axis(axis.input_id)
def axis1(event, vjoy):
    global g_last_value

    delta = event.value - g_last_value
    if abs(delta) > step_size.value:
        g_last_value = event.value
        if delta > 0:
            gremlin.macro.MacroManager().queue_macro(inc_macro)
        else:
            gremlin.macro.MacroManager().queue_macro(dec_macro)

