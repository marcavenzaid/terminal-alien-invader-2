"""Reading the keyboard. Windows only: keys come in through msvcrt and the Windows API."""
import ctypes
import msvcrt

from terminal_alien_invader_2.config import (
    ARROW_PREFIXES,
    KEY_ESCAPE,
    KEY_LEFT,
    KEY_RIGHT,
    MOVEMENT_DIRECTIONS,
    VK_A,
    VK_D,
    VK_LEFT,
    VK_RIGHT,
)
from terminal_alien_invader_2.player import move_player
from terminal_alien_invader_2.state import state

# Resolved once. restype keeps the SHORT the function returns from being widened
# into a value whose extra sign bits could confuse the test in is_key_down.
GET_ASYNC_KEY_STATE = ctypes.windll.user32.GetAsyncKeyState
GET_ASYNC_KEY_STATE.restype = ctypes.c_short
KEY_DOWN_BIT = 0x8000


def player_control():
    """Note every key pressed since the last frame, then move the ship.

    Reading is non-blocking. If nothing was typed the function returns at once
    and the ship stays where it is. Returns False when the player asked to quit,
    which ends the game loop.
    """
    while msvcrt.kbhit():
        key = msvcrt.getwch()

        if key in ARROW_PREFIXES:
            key = msvcrt.getwch()
            if key == KEY_LEFT:
                state.held_movement_keys.add(VK_LEFT)
            elif key == KEY_RIGHT:
                state.held_movement_keys.add(VK_RIGHT)
            continue

        key = key.lower()
        if key == "a":
            state.held_movement_keys.add(VK_A)
        elif key == "d":
            state.held_movement_keys.add(VK_D)
        elif key == KEY_ESCAPE:  # Esc quits.
            return False

    move_held_keys()
    return True


def move_held_keys():
    """Move the ship one cell for each steering key that is still held down.

    Called every frame, so a held key moves the ship on every frame from the one
    it was pressed on. None of the pause Windows leaves before a held key starts
    repeating its character (e.g. 'a...aaaaaaaaaaa' when pressing 'a'), and a steady 
    speed instead of its repeat rate. Keys the keyboard reports as released are forgotten.
    """
    for virtual_key in sorted(state.held_movement_keys):  # A copy, so it can be edited.
        if is_key_down(virtual_key):
            move_player(MOVEMENT_DIRECTIONS[virtual_key])
        else:
            state.held_movement_keys.discard(virtual_key)


def is_key_down(virtual_key):
    """Report whether a key is physically held down at this instant.

    GetAsyncKeyState answers from the keyboard itself rather than from the
    console's character stream, so it knows nothing of the repeat delay and
    repeat rate Windows applies to a held key.
    """
    return bool(GET_ASYNC_KEY_STATE(virtual_key) & KEY_DOWN_BIT)


def discard_keys():
    """Read and throw away every key typed since the last call.

    Used while the round-end text is up, so the next round is not started with a
    backlog of keys. Returns False if Esc was among them, which ends the game.
    """
    while msvcrt.kbhit():
        if msvcrt.getwch() == KEY_ESCAPE:
            return False
    return True
