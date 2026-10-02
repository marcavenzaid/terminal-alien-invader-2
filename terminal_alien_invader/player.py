"""The player's ship: spawning, steering, firing, and being destroyed."""
import time

from terminal_alien_invader.config import (
    PLAYER_ATTACK_INTERVAL,
    PLAYER_HITBOX_RADIUS,
    PLAYER_MAX_X,
    PLAYER_MIN_X,
    PLAYER_SHIP,
    PLAYER_SHIP_EXPLOSION,
)
from terminal_alien_invader.state import state


def spawn_player():
    """Spawn the player's ship at the bottom of the main display."""
    state.world[state.player_x][state.player_y] = PLAYER_SHIP


def destroy_player():
    """Blow the ship up where it stands, once the last of its health is gone.

    The wreck is left standing in the ship's cell rather than entered among the
    explosions to be erased when its moment is up, because there is no moment to
    wait out. The round ends on this frame and the world is left frozen as it
    is, wreck and all, for as long as it is being closed over.
    """
    state.player_destroyed = True
    state.world[state.player_x][state.player_y] = PLAYER_SHIP_EXPLOSION


def move_player(dx):
    """Shift the ship dx cells sideways, clamped to the main display.

    Nothing is redrawn unless the ship actually changes column, so a key held
    against either edge of the display costs no output at all.
    """
    # Erase the ship where it was, then draw it where it now is.
    state.world[state.player_x][state.player_y] = ' '

    # Where the ship ends up, clamped to the main display area. 
    # Against an edge this is the column it already occupies.
    state.player_x = max(min(PLAYER_MAX_X, state.player_x + dx), PLAYER_MIN_X)
    state.world[state.player_x][state.player_y] = PLAYER_SHIP


def player_auto_attack():
    """Fire a projectile from the ship's nose once the weapon has cooled down.

    Called every frame. Shots are paced by wall-clock time rather than a frame
    count, so the fire rate stays the same if the loop ever runs at a different
    speed.
    """
    now = time.monotonic()
    if now - state.player_last_attack < PLAYER_ATTACK_INTERVAL:
        return

    state.player_last_attack = now
    state.player_projectiles.append([state.player_x, state.player_y - 1])


def move_player_projectiles():
    """Climb every projectile up the screen and drop the ones that left the display.

    The projectiles are deliberately left undrawn at their new positions. 
    The cell a projectile just entered still holds whatever was standing there,
    which is exactly what collision_detection needs to read. 
    It draws the projectiles that survive the check.
    """

    # Erase the projectiles at their current positions before moving them.
    for projectile_x, projectile_y in state.player_projectiles:
        state.world[projectile_x][projectile_y] = ' '

    # Move every projectile up one cell.
    for projectile in state.player_projectiles:
        projectile[1] -= 1

    updated_projectiles = []
    for projectile in state.player_projectiles:
        if projectile[1] >= 0:
            updated_projectiles.append(projectile)
    state.player_projectiles.clear()
    state.player_projectiles.extend(updated_projectiles)


def hits_player(x, y):
    """Report whether the cell at (x, y) is one a shot would strike the ship in.

    The hitbox is worked out from where the ship stands rather than read out of
    the world, because it reaches past the one cell the ship is drawn in. 
    The cells PLAYER_HITBOX_RADIUS either side of it are left empty for whatever
    else is passing through them, so there is nothing in them to recognise the ship by. 
    It is a row of cells and not a block of them, the ship being a single row tall, 
    so a shot one row short of the ship has yet to reach it.
    """
    return y == state.player_y and abs(x - state.player_x) <= PLAYER_HITBOX_RADIUS
