"""The short-lived marks left by explosions and by shots striking their target."""
import time

from terminal_alien_invader.config import (
    PLAYER_PROJECTILE_EXPLOSION_EFFECT,
    PLAYER_PROJECTILE_EXPLOSION_EFFECT_DURATION,
)
from terminal_alien_invader.state import state


def show_player_projectile_explosion_effect(struck_x, struck_y, now):
    """Burst a player's shot against what it struck at (struck_x, struck_y).

    What it struck is a ship of the army or a cell of a boss's barrier. 
    The burst goes in the cell directly in front of it, the one facing the player,
    which is the side every shot comes up at it from. 
    It is only the flash of the hit, 
    and is erased once its moment is up as the marks destroyed ships leave are 
    (see clear_finished_explosions).

    It is only put into an empty cell. The ranks stand one row behind another,
    so a ship of the row in front may have stepped into that cell this frame,
    and drawn over, it would be rubbed out of the world. Anything else standing
    there is left to be seen rather than hidden under the flash.
    """
    x, y = struck_x, struck_y + 1
    if state.world[x][y] != ' ':
        return

    # The cell is empty, so any record still held for it is of a mark already
    # gone from it. Left in place, one of an earlier burst would erase this one
    # when its own, earlier, time was up, the two being drawn alike.
    state.explosions[:] = [
        explosion
        for explosion in state.explosions
        if (explosion[0], explosion[1]) != (x, y)
    ]

    state.world[x][y] = PLAYER_PROJECTILE_EXPLOSION_EFFECT
    clear_time = now + PLAYER_PROJECTILE_EXPLOSION_EFFECT_DURATION
    state.explosions.append([x, y, clear_time, PLAYER_PROJECTILE_EXPLOSION_EFFECT])


def clear_finished_explosions():
    """Erase the explosion marks that have had their moment on screen."""

    now = time.monotonic()
    burning_explosions = []
    for explosion in state.explosions:
        explosion_x, explosion_y, clear_time, explosion_character = explosion
        if now < clear_time:
            burning_explosions.append(explosion)
        elif state.world[explosion_x][explosion_y] == explosion_character:
            # Only the explosion's own mark is erased. Anything drawn over that
            # cell since owns it now and is left alone.
            state.world[explosion_x][explosion_y] = ' '
    state.explosions.clear()
    state.explosions.extend(burning_explosions)
