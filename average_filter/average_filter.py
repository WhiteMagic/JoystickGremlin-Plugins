from collections import deque
import threading
import time

import gremlin
from gremlin.user_plugin import *


mode = ModeVariable("Mode", "The mode in which to use this mapping")

vjoy_axis = VirtualInputVariable(
        "Virtual output axis",
        "The vJoy axis to send the filtered output to.",
        [gremlin.common.InputType.JoystickAxis]
)

joy_axis = PhysicalInputVariable(
        "Physical input axis",
        "The physical input axis being filtered.",
        [gremlin.common.InputType.JoystickAxis]
)

sample_size = IntegerVariable(
        "Number of samples",
        "Number of samples to use to compute the average.",
        5,
        1,
        50
)

update_rate = IntegerVariable(
        "Update rate (ms)",
        "Time between expected updates in milliseconds",
        250,
        10,
        5000
)


# Global variables
g_samples = deque([], maxlen=sample_size.value)
g_last_value = 0.0
g_last_update = time.time()
g_thread = None
g_vjoy = gremlin.joystick_handling.VJoyProxy()

d_axis = joy_axis.create_decorator(mode.value)


def update_thread():
    global g_samples
    rate = update_rate.value / 1000.0

    while True:
        # Repeat last value
        if g_last_update + rate < time.time():
            g_samples.append(g_last_value)
            update_vjoy()

        # Ensure the thread terminates
        if (g_last_update + (rate * g_samples.maxlen)) < time.time():
            return

        time.sleep(rate)


def average():
    return sum(g_samples) / len(g_samples)


def update_vjoy():
    global g_vjoy
    g_vjoy[vjoy_axis.vjoy_id].axis(vjoy_axis.input_id).value = average()


@d_axis.axis(joy_axis.input_id)
def axis_cb(event):
    global g_samples, g_last_value, g_last_update, g_thread

    g_last_value = event.value
    g_last_update = time.time()
    g_samples.append(event.value)
    update_vjoy()

    if g_thread is None or not g_thread.is_alive():
        g_thread = threading.Thread(target=update_thread)
        g_thread.start()


