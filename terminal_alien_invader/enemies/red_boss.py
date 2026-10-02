"""The red boss: its changing pace, its teleports, and its frenzy mode."""
import random
import time

from terminal_alien_invader.config import (
    ENEMY_RED_BOSS,
    ENEMY_RED_BOSS_FRENZY_MODE_CHANGE_DIRECTION_INTERVAL,
    ENEMY_RED_BOSS_FRENZY_MODE_COLORS,
    ENEMY_RED_BOSS_FRENZY_MODE_DURATION,
    ENEMY_RED_BOSS_FRENZY_MODE_INTERVAL_RANGE,
    ENEMY_RED_BOSS_FRENZY_MODE_TELEPORT_INTERVAL_RANGE,
    ENEMY_RED_BOSS_MOVE_INTERVAL_CHANGE_INTERVAL,
    ENEMY_RED_BOSS_MOVE_INTERVAL_RANGE,
    ENEMY_RED_BOSS_TELEPORT_INTERVAL_RANGE,
    ENEMY_ZONE_MAX_X,
    ENEMY_ZONE_MAX_Y,
    ENEMY_ZONE_MIN_X,
    ENEMY_ZONE_MIN_Y,
)
from terminal_alien_invader.enemies.attack import random_attack_delay
from terminal_alien_invader.enemies.bosses import boss_barrier_stands, carry_enemy_boss, enemy_boss_move_interval
from terminal_alien_invader.state import state


def update_enemy_red_boss_move_interval():
    """Re-draw the pace the red boss marches at, once the one it holds has had its run.

    The red boss keeps a drawn pace for ENEMY_RED_BOSS_MOVE_INTERVAL_CHANGE_INTERVAL
    seconds and is then given another drawn from the same range, so it goes on
    changing speed for as long as it is marching rather than crossing its zone at
    the one pace. A pace of zero is a step every frame and the far end of the
    range is a crawl, so the two of them are what it lurches between.

    Called every frame just before move_enemy_bosses, but held off for as long as boss
    1's own barrier stands, so the re-drawing waits out that barrier along with
    the marching itself: a pace drawn while the red boss still stood behind it would be
    part spent, or spent outright, by the time it had a step to take.
    """
    if boss_barrier_stands(ENEMY_RED_BOSS):
        return

    now = time.monotonic()

    if now < state.enemy_red_boss_move_interval_next_change:
        return

    state.enemy_red_boss_move_interval = random.uniform(*ENEMY_RED_BOSS_MOVE_INTERVAL_RANGE)
    state.enemy_red_boss_move_interval_next_change = now + ENEMY_RED_BOSS_MOVE_INTERVAL_CHANGE_INTERVAL


def teleport_enemy_red_boss():
    """Carry the red boss from the cell it holds to another drawn from the army's zone.

    Marching along one row is not all the red boss does. Every few seconds it vanishes
    from where it stands and appears somewhere else entirely, its column and its
    row both drawn afresh, so it has to be hunted about the zone rather than
    tracked along the one row. It marches on from wherever it lands, so a jump
    hands it a new row to cross as well as a new place on it.

    The cell is drawn from ENEMY_ZONE_MIN_X to ENEMY_ZONE_MAX_X and
    ENEMY_ZONE_MIN_Y to ENEMY_ZONE_MAX_Y, which is the stretch of the display the
    army holds and no more, so a jump only ever puts the red boss where some ship of the
    army could have stood, never down among the player's own rows or off an edge
    of the display. The wait until the next is re-drawn after every jump, so
    they come at no settled rhythm, and drawn from a quicker range while the red boss
    is in a frenzy (see random_teleport_delay).

    Called every frame just before move_enemy_bosses, but held off for as long as boss
    1's own barrier stands, as its marching and its pace are: a boss still
    sheltering has not been reached yet, and a jump out from behind that barrier
    would leave the wall standing in front of nothing. The wait is armed while it
    shelters rather than left to run down, so the red boss is not carried off on the
    very frame that barrier comes down.

    Called, as the marching is, from the part of the frame where none of the
    projectiles is drawn in the world, so the boss is moved among empty cells and a
    shot it has just appeared in front of meets it there when the projectiles are
    checked against what they flew into.
    """
    now = time.monotonic()

    if boss_barrier_stands(ENEMY_RED_BOSS):
        # Still sheltering, so still standing where it spawned. The wait is kept a
        # full one ahead of now for as long as that lasts, so it is only ever run
        # down once the barrier is gone.
        state.enemy_red_boss_next_teleport = now + random_teleport_delay()
        return

    if now < state.enemy_red_boss_next_teleport:
        return

    state.enemy_red_boss_next_teleport = now + random_teleport_delay()

    for boss in state.enemy_bosses:
        if boss[5] != ENEMY_RED_BOSS:
            continue

        # A boss that is no longer standing where its record has it has been
        # destroyed, and there is nothing left to carry.
        if state.world[boss[0]][boss[1]] != ENEMY_RED_BOSS:
            return

        carry_enemy_boss(
            boss,
            random.randint(ENEMY_ZONE_MIN_X, ENEMY_ZONE_MAX_X),
            random.randint(ENEMY_ZONE_MIN_Y, ENEMY_ZONE_MAX_Y),
        )
        return


def random_teleport_delay():
    """Pick how long the red boss waits before its next teleport, in seconds.

    The wait is drawn from ENEMY_RED_BOSS_TELEPORT_INTERVAL_RANGE, or from
    ENEMY_RED_BOSS_FRENZY_MODE_TELEPORT_INTERVAL_RANGE while the red boss is in a
    frenzy, so it is carried about the zone all the more often for as long as
    one lasts.
    """
    if state.enemy_red_boss_in_frenzy_mode():
        return random.uniform(*ENEMY_RED_BOSS_FRENZY_MODE_TELEPORT_INTERVAL_RANGE)
    return random.uniform(*ENEMY_RED_BOSS_TELEPORT_INTERVAL_RANGE)


def change_enemy_red_boss_direction():
    """Turn the red boss about every so often, for as long as it is in a frenzy.

    Out of a frenzy the red boss only turns at the ends of the stretch it marches, as
    every boss does (see step_enemy_boss). In one it also turns about of its own
    accord, wherever it has got to, the wait between one turn and the next drawn
    from ENEMY_RED_BOSS_FRENZY_MODE_CHANGE_DIRECTION_INTERVAL and re-drawn after
    every one, so it lurches back and forth across the display at no settled
    rhythm rather than sweeping it from end to end. Only the way it is headed is
    turned about: the steps that carry it are left to come at their own pace.

    Called every frame just before move_enemy_bosses, so the step due this frame
    is taken the new way. Out of a frenzy the wait is kept a full
    one ahead of now rather than left to run down, as the wait for a teleport is
    while the red boss shelters, so it is only ever run down in a frenzy, never left
    over from before one.
    """
    now = time.monotonic()

    if not state.enemy_red_boss_in_frenzy_mode():
        state.enemy_red_boss_next_direction_change = now + random.uniform(
            *ENEMY_RED_BOSS_FRENZY_MODE_CHANGE_DIRECTION_INTERVAL
        )
        return

    if now < state.enemy_red_boss_next_direction_change:
        return

    state.enemy_red_boss_next_direction_change = now + random.uniform(
        *ENEMY_RED_BOSS_FRENZY_MODE_CHANGE_DIRECTION_INTERVAL
    )

    for boss in state.enemy_bosses:
        if boss[5] == ENEMY_RED_BOSS:
            boss[2] = -boss[2]


def update_enemy_red_boss_frenzy_mode():
    """Put the red boss into a frenzy when one is due, and move one on through its colours.

    A frenzy sets in every so many seconds, the wait from the start of one to
    the start of the next drawn from ENEMY_RED_BOSS_FRENZY_MODE_INTERVAL_RANGE and
    re-drawn every time, and wears off on its own once
    ENEMY_RED_BOSS_FRENZY_MODE_DURATION seconds of that wait are up (see GameState.enemy_red_boss_in_frenzy_mode). 
    So a frenzy has only to be set going, and its pace seen to take hold at once. 
    The red boss's waits on its next teleport, step and shot were armed at its own pace, so they are armed afresh at the frenzy's. 
    Left to run down, a teleport armed at its own pace could be further off than the whole frenzy lasts. 
    Nothing has to be put back as a frenzy wears off. 
    Each wait armed at its pace is re-armed at the red boss's own as it comes due.

    Each frenzy opens on the first of ENEMY_RED_BOSS_FRENZY_MODE_COLORS 
    and moves on to the next on every frame it lasts, back round to the first after the last. 
    The boss is drawn in whichever it has got to, and so is any bolt it fires on that frame (see render_world and pick_shot).

    Called every frame, before the army fires and marches, so the red boss is at the
    frenzy's pace and in its colours from the very frame one sets in. 
    Held off, as the red boss's marching and its teleports are, for as long as its own barrier stands. 
    The wait is armed while it shelters rather than left to run down, 
    so the red boss is not thrown into a frenzy on the very frame that barrier comes down.
    """
    now = time.monotonic()

    if boss_barrier_stands(ENEMY_RED_BOSS):
        # Still sheltering. The wait is kept a full one ahead of now for as long
        # as that lasts, so it is only ever run down once the barrier is gone.
        state.enemy_red_boss_next_frenzy_mode = now + random.uniform(*ENEMY_RED_BOSS_FRENZY_MODE_INTERVAL_RANGE)
        return

    if now < state.enemy_red_boss_next_frenzy_mode:
        # No frenzy sets in on this frame, so one already under way moves on to
        # its next colour.
        if state.enemy_red_boss_in_frenzy_mode():
            state.enemy_red_boss_frenzy_mode_color_index += 1
            state.enemy_red_boss_frenzy_mode_color_index %= len(ENEMY_RED_BOSS_FRENZY_MODE_COLORS)
        return

    state.enemy_red_boss_next_frenzy_mode = now + random.uniform(*ENEMY_RED_BOSS_FRENZY_MODE_INTERVAL_RANGE)
    state.enemy_red_boss_frenzy_mode_end = now + ENEMY_RED_BOSS_FRENZY_MODE_DURATION
    state.enemy_red_boss_frenzy_mode_color_index = 0

    # The frenzy has set in, so each of these comes out at its pace.
    state.enemy_red_boss_next_teleport = now + random_teleport_delay()
    for boss in state.enemy_bosses:
        if boss[5] != ENEMY_RED_BOSS:
            continue

        boss[6] = now + enemy_boss_move_interval(ENEMY_RED_BOSS)

        # Its next shot is kept against the cell it stands in, as every ship's
        # is (see enemy_auto_attack).
        cell = (boss[0], boss[1])
        if cell in state.enemy_next_attack:
            state.enemy_next_attack[cell] = now + random_attack_delay(ENEMY_RED_BOSS)
