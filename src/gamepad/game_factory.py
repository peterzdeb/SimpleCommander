#!/usr/bin/env python3
from gamepad.gamepad_controller import GamepadController


__game = None

def get_game(height=None, width=None, invaders_count=None, notify_callback=print):
    global __game

    if not __game:
        __game = GamepadController(notify_callback=notify_callback)
    return __game