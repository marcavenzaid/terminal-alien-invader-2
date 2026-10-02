"""How the army fires: which ship in each column shoots, when, and with what."""
import random
import time

from terminal_alien_invader.config import (
    ENEMY_ATTACK_INTERVAL_RANGES,
    ENEMY_RED_BOSS,
    ENEMY_RED_BOSS_FRENZY_MODE_ATTACK_INTERVAL,
    ENEMY_RED_BOSS_FRENZY_MODE_PROJECTILE,
    ENEMY_BOSS_CHARACTERS,
    ENEMY_CHARACTERS,
    ENEMY_PROJECTILES,
    ENEMY_PROJECTILE_DAMAGES,
    MAIN_DISPLAY_START_X,
    XCELLS,
    YCELLS,
)
from terminal_alien_invader.enemies.bosses import boss_barrier_stands
from terminal_alien_invader.state import state


def enemy_auto_attack():
    """Fire from the front ship of every column whose turn has come round.

    Called every frame. Only the ship at the front in a column has a clear shot at the player, 
    so it is the only one there that fires. The ships stacked behind it hold until it is 
    destroyed and one of them becomes the front. Each column keeps its own countdown, 
    re-rolled after every shot, so the army fires in a ragged rhythm rather than in volleys. 
    Like the player's, the shots are paced by wall-clock time rather than a frame count, 
    so the rate of fire stays the same if the loop ever runs at a different speed.

    The countdown belongs to the ship and not to the column it happens to be
    standing in, because the rows march through the columns rather than standing
    in them. A ship carries its countdown with it as it goes (see
    shift_enemy_rank), so it fires at the rate its kind was given wherever it has
    got to, rather than picking up whatever the column it stepped into was left
    holding and firing again the moment it arrives.

    A boss is the exception: its own barrier walls in its shot as surely as the
    player's, so it holds its fire for as long as that one line stands, whatever
    the other bosses' barriers are doing, and then waits out a full interval as
    any column just given a shooter does.
    """
    now = time.monotonic()

    for x in range(MAIN_DISPLAY_START_X, XCELLS):
        front_y = find_front_enemy(x)

        if front_y is None:
            # Nothing in this column to take the shot. Its countdown is left
            # running for whichever ship marches into the column next.
            continue

        front_enemy = state.world[x][front_y]

        if front_enemy in ENEMY_BOSS_CHARACTERS and boss_barrier_stands(front_enemy):
            # A boss has no shot out through its own barrier. Dropping the
            # countdown leaves the column to be given a fresh one once that
            # barrier is down, so a boss does not open fire on the very frame it
            # comes down.
            state.enemy_next_attack.pop((x, front_y), None)
            continue

        if (x, front_y) not in state.enemy_next_attack:
            # A ship that has only just reached the front waits out a full
            # interval before its first shot, so neither the army at the start
            # of the game nor a ship promoted by a kill opens fire at once.
            state.enemy_next_attack[(x, front_y)] = now + random_attack_delay(front_enemy)
            continue

        if now < state.enemy_next_attack[(x, front_y)]:
            continue

        state.enemy_next_attack[(x, front_y)] = now + random_attack_delay(front_enemy)

        # A ship standing on the last row has nowhere to put a shot.
        if front_y + 1 < YCELLS:
            state.enemy_projectiles.append(
                [
                    x,
                    front_y + 1,
                    pick_shot(front_enemy),
                    ENEMY_PROJECTILE_DAMAGES[front_enemy],
                ]
            )


def pick_shot(enemy):
    """Pick the character the next shot from this kind of ship is drawn with.

    A kind whose shot is a tuple of characters, as the orange boss's and the green boss's are,
    fires one of them at random. A kind with a single character always fires
    that one. The red boss in a frenzy fires its bolt out of
    ENEMY_RED_BOSS_FRENZY_MODE_PROJECTILE instead, in whichever of the frenzy's
    colours it is drawn in itself on this frame (see
    update_enemy_red_boss_frenzy_mode).
    """
    if enemy == ENEMY_RED_BOSS and state.enemy_red_boss_in_frenzy_mode():
        return ENEMY_RED_BOSS_FRENZY_MODE_PROJECTILE[state.enemy_red_boss_frenzy_mode_color_index]

    shot = ENEMY_PROJECTILES[enemy]
    if isinstance(shot, tuple):
        return random.choice(shot)
    return shot


def random_attack_delay(enemy):
    """Pick how long a column waits before its next shot, in seconds.

    The wait is drawn from the range that kind of ship fires at, so a column
    slows down or speeds up as the ship at its front changes, and each boss
    keeps its own rhythm. The red boss in a frenzy has no range to draw from, and
    waits ENEMY_RED_BOSS_FRENZY_MODE_ATTACK_INTERVAL between one shot and the
    next.
    """
    if enemy == ENEMY_RED_BOSS and state.enemy_red_boss_in_frenzy_mode():
        return ENEMY_RED_BOSS_FRENZY_MODE_ATTACK_INTERVAL
    return random.uniform(*ENEMY_ATTACK_INTERVAL_RANGES[enemy])


def find_front_enemy(x):
    """Return the row of the frontmost enemy ship in column x, or None if it holds none.

    The front of the army is its lowest rank, the one nearest the player, so the
    column is read from the bottom of the display upwards and the first ship met
    is the one with a clear shot.
    """
    for y in range(YCELLS - 1, -1, -1):
        if state.world[x][y] in ENEMY_CHARACTERS:
            return y
    return None


def move_enemy_projectiles():
    """Drop every enemy projectile down the screen and drop the ones that left the display.

    As with the player's shots, the projectiles are deliberately left undrawn at
    their new positions: the cell a projectile just entered still holds whatever
    was standing there, which is what collision_detection needs to read, and it
    draws the projectiles that survive the check.
    """

    # Erase the projectiles at their current positions before moving them.
    for projectile_x, projectile_y, _, _ in state.enemy_projectiles:
        state.world[projectile_x][projectile_y] = ' '

    # Move every projectile down one cell.
    for projectile in state.enemy_projectiles:
        projectile[1] += 1

    updated_projectiles = []
    for projectile in state.enemy_projectiles:
        if projectile[1] < YCELLS:
            updated_projectiles.append(projectile)
    state.enemy_projectiles.clear()
    state.enemy_projectiles.extend(updated_projectiles)
