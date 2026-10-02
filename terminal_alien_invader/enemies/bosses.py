"""The bosses every boss shares: spawning, marching, being hit, and their barriers."""
import random
import time

from terminal_alien_invader.config import (
    ENEMY_RED_BOSS,
    ENEMY_RED_BOSS_FRENZY_MODE_MOVE_INTERVAL,
    ENEMY_BOSS_BARRIER_CHARACTERS,
    ENEMY_BOSS_BARRIER_WIDTH,
    ENEMY_BOSS_BARRIER_Y,
    ENEMY_BOSS_CHARACTERS,
    ENEMY_BOSS_HITBOX_RADIUS,
    ENEMY_BOSS_MOVE_INTERVALS,
    ENEMY_LAST_BOSS,
    ENEMY_LESSER_BOSSES,
    ENEMY_MAX_HEALTHS,
    ENEMY_STARTING_Y,
    MAIN_DISPLAY_START_X,
    MAIN_DISPLAY_WIDTH,
    XCELLS,
)
from terminal_alien_invader.state import state


def spawn_bosses():
    """Spawn the bosses across the army's back row, in a random order.

    They take the row furthest from the player, and the whole width of the main
    display is split into as many equal zones as there are bosses, one boss
    standing at the middle of each. That spreads them evenly across the display,
    out to its own edges at the ends. Which boss takes which zone is re-drawn
    every game.

    The lesser bosses march the zone they spawned in and no further, so the two
    of them keep to their own stretches of the row and never cross. The last
    boss is not held to its zone: it only ever marches once the other two have
    been destroyed and there is nothing left on the row to keep out of the way
    of, so it is given the whole width of the main display to sweep instead. Nor
    is it held to the row it is spawned on, being teleported about the army's
    whole zone every few seconds once it is free to move (see
    teleport_enemy_red_boss).

    Standing at the back, a boss has the ranks and its own barrier in front of
    it, so it has no clear shot until the ranks have been destroyed.

    Each boss is also given a barrier in the clear row ahead of it, which stands
    for as long as whatever shelters that boss does (see update_boss_barriers),
    and the ends of its zone, which is the stretch of the row it marches once its
    own barrier is down and it leaves the place it spawned in (see
    move_enemy_bosses).
    """
    y = ENEMY_STARTING_Y
    bosses = random.sample(ENEMY_BOSS_CHARACTERS, len(ENEMY_BOSS_CHARACTERS))

    # The width of one zone. Counted in the main display's own cells, which the
    # zones take between them end to end, so the ones at the ends run right out
    # to the display's edges. It is fractional where the cells do not divide
    # evenly among the zones.
    zone_width = MAIN_DISPLAY_WIDTH / len(bosses)

    for place, boss in enumerate(bosses):
        # The first and last cells of this boss's zone, which are the ends it
        # turns around at. Each zone picks up on the cell after the one before
        # it left off, so the zones cover the display between them without
        # overlapping and the bosses never cross.
        zone_min_x = MAIN_DISPLAY_START_X + round(place * zone_width)
        zone_max_x = MAIN_DISPLAY_START_X + round((place + 1) * zone_width) - 1

        # The boss spawns at the middle of its zone, so it has the same stretch
        # of it to march whichever way it is sent off.
        boss_x = (zone_min_x + zone_max_x) // 2
        state.world[boss_x][y] = boss
        state.enemy_health[(boss_x, y)] = ENEMY_MAX_HEALTHS[boss]
        state.boss_count += 1
        if boss in ENEMY_LESSER_BOSSES:
            state.lesser_boss_count += 1

        # The zone is only what the lesser bosses are held to. The last boss
        # spawned at the middle of its zone with the rest, but marches the whole
        # main display: by the time it has a step to take the others are wrecks,
        # so there is nothing for it to run into out there.
        if boss == ENEMY_LAST_BOSS:
            zone_min_x = MAIN_DISPLAY_START_X
            zone_max_x = XCELLS - 1

        # Neighbouring zones send their bosses opposite ways, the first of them
        # to the left, as the ranks' rows are sent.
        direction = -1 if place % 2 == 0 else 1
        state.enemy_bosses.append([boss_x, y, direction, zone_min_x, zone_max_x, boss, 0.0])

        # The barrier is hung centred on the boss's own column, and shifted back
        # onto the display if a boss standing near an edge would push it off.
        barrier_x = boss_x - ENEMY_BOSS_BARRIER_WIDTH // 2
        barrier_x = min(max(barrier_x, MAIN_DISPLAY_START_X), XCELLS - ENEMY_BOSS_BARRIER_WIDTH)
        state.enemy_boss_barriers.append([barrier_x, ENEMY_BOSS_BARRIER_Y, boss])


def boss_hit_at(x, y):
    """Return the (x, y) of the boss a shot in the cell at (x, y) strikes, or None.

    Like hits_player, the hitbox is worked out from where each boss stands, the
    cells ENEMY_BOSS_HITBOX_RADIUS either side of it holding nothing to know it
    by. A boss whose record no longer matches the world has been destroyed and
    is passed over.
    """
    for boss_x, boss_y, _, _, _, character, _ in state.enemy_bosses:
        if (
            y == boss_y
            and abs(x - boss_x) <= ENEMY_BOSS_HITBOX_RADIUS
            and state.world[boss_x][boss_y] == character
        ):
            return boss_x, boss_y
    return None


def move_enemy_bosses():
    """Step every boss one cell along the way it is travelling.

    A boss stands still for as long as its own barrier does, as it holds its fire, 
    and so is only set marching once the line in front of it has come down.
    The lesser bosses once the last of the ranks has been destroyed, 
    and the last boss once both of them have been (see update_boss_barriers).

    A boss keeps to the stretch of the back row it was given, marching to one end of it, 
    taking that end, and turning there: the next step it is due is the one back the other way. 
    For the lesser bosses that stretch is the zone each spawned in, 
    so the two of them stay spread across the army's width and never cross one another, 
    and neighbouring zones were sent opposite ways, so they do not sweep the row in step either. 
    For the last boss it is the whole main display, which it has to itself by then.

    Each boss is paced by the interval its own kind is given and keeps its own countdown, 
    so a quick kind crosses its zone many times over while a slow one is still on its way across. 
    The red boss's interval is not one it holds for the round but one re-drawn every few seconds,
    so it is brought up to date before this is called (see update in game.py).

    Marching is not all that moves the red boss.
    It is also teleported about the army's zone every few seconds, and in a frenzy turned about every so often.
    Both are taken before this is called as well (see enemies/red_boss.py),
    so a jump due this frame is made from where the boss stood rather than from the cell one step along,
    and the step due this frame is taken the new way.
    The row it lands on is the row it marches from then on.

    Called every frame, but the steps themselves are paced by wall-clock time as everything else that moves on its own is.
    """
    now = time.monotonic()

    for boss in state.enemy_bosses:
        if boss_barrier_stands(boss[5]):
            # Still sheltering, so still standing where it spawned. Its
            # countdown is untouched and so is still zero, which is what sets it
            # marching the moment its own line does come down.
            continue

        if now < boss[6]:
            continue

        boss[6] = now + enemy_boss_move_interval(boss[5])
        step_enemy_boss(boss)


def enemy_boss_move_interval(boss_character):
    """Return how long this boss waits between one step and the next, in seconds.

    Every bosses other than the red boss marches at the one interval its kind was given. 
    The red boss marches at whatever its pace was last re-drawn as, 
    which update_enemy_red_boss_move_interval is what keeps current, 
    except in a frenzy, when it marches at ENEMY_RED_BOSS_FRENZY_MODE_MOVE_INTERVAL instead.
    """
    if boss_character == ENEMY_RED_BOSS:
        if state.enemy_red_boss_in_frenzy_mode():
            return ENEMY_RED_BOSS_FRENZY_MODE_MOVE_INTERVAL
        return state.enemy_red_boss_move_interval

    return ENEMY_BOSS_MOVE_INTERVALS[boss_character]


def step_enemy_boss(boss):
    """Carry one boss a single cell the way it is travelling.

    A boss marches along whichever row it is standing on, which is the one it spawned on for every boss but the red boss, 
    and for that one whichever its last teleport left it on (see teleport_enemy_red_boss).

    A boss that is no longer standing where its record has it has been destroyed, and there is nothing left to carry.

    Called from the part of the frame where none of the projectiles is drawn in the world, 
    so the boss is moved among empty cells, and a shot it has just stepped in front of 
    meets it there when the projectiles are checked against what they flew into.
    """
    boss_x, boss_y, direction, min_x, max_x, character, _ = boss

    if state.world[boss_x][boss_y] != character:
        return

    next_x = boss_x + direction
    if not min_x <= next_x <= max_x:
        # The boss is standing on the end of its zone it was marching towards,
        # so this is the step that sends it back the other way.
        direction = -direction
        boss[2] = direction
        next_x = boss_x + direction
        if not min_x <= next_x <= max_x:
            # A zone one column wide leaves the boss nowhere to march.
            return

    carry_enemy_boss(boss, next_x, boss_y)


def carry_enemy_boss(boss, next_x, next_y):
    """Move one boss out of the cell it holds and into another, with all it owns.

    What the two ways a boss is moved have in common: the single step of its
    march, and the jump the red boss is carried off on. The caller is what settles the
    cell and what checks the boss is still standing to be moved at all. 
    This only carries it there.

    The boss takes its own countdown along with it, as the ranks do, and drops
    anything the cell it is moving into was left holding: a countdown left there
    by a ship destroyed earlier in the round is long overdue by the time the
    bosses are on the move, and would have the boss firing on nearly every move
    it made.

    What the boss has left of its health travels with it in the same way, so the
    damage it has taken is not left behind on the cell it fought on.
    """
    boss_x, boss_y, character = boss[0], boss[1], boss[5]

    due = state.enemy_next_attack.pop((boss_x, boss_y), None)
    state.enemy_next_attack.pop((next_x, next_y), None)
    if due is not None:
        state.enemy_next_attack[(next_x, next_y)] = due

    remaining = state.enemy_health.pop((boss_x, boss_y), None)
    state.enemy_health.pop((next_x, next_y), None)
    if remaining is not None:
        state.enemy_health[(next_x, next_y)] = remaining

    state.world[boss_x][boss_y] = ' '
    state.world[next_x][next_y] = character
    boss[0] = next_x
    boss[1] = next_y


def update_boss_barriers():
    """Keep each boss's barrier standing for as long as it is owed one.

    Called every frame, after the projectiles have moved and before they are
    checked against what they flew into, so a shot that has just climbed into a
    barrier meets it there and is stopped. A line is held in its cells every
    frame rather than drawn once, so that it stands whole again whatever has
    been drawn over it since.

    The barriers come down a wave at a time, so the army is fought through in
    three. The ranks hold up the lesser bosses' barriers. The moment the last
    ship of the ranks is destroyed those two come down together, leaving bosses
    2 and 3 open to the shots they have been sheltered from and free to return
    them. Those two in turn hold up the last boss's, which stands on through
    that fight and comes down only once both of them have been destroyed, so
    the red boss is met last and on its own.
    """
    standing = []
    for barrier in state.enemy_boss_barriers:
        barrier_x, barrier_y, boss_character = barrier

        # The ranks hold up every barrier. The last boss's is held up by the
        # lesser bosses as well, and so outlasts theirs.
        held_up = state.non_boss_enemy_count > 0
        if boss_character == ENEMY_LAST_BOSS:
            held_up = held_up or state.lesser_boss_count > 0

        barrier_character = ENEMY_BOSS_BARRIER_CHARACTERS[boss_character]
        for offset in range(ENEMY_BOSS_BARRIER_WIDTH):
            state.world[barrier_x + offset][barrier_y] = (
                barrier_character if held_up else ' '
            )

        if held_up:
            standing.append(barrier)

    # Dropping the barriers that have come down is what keeps them from being
    # taken down again on every frame that follows.
    state.enemy_boss_barriers[:] = standing


def boss_barrier_stands(boss_character):
    """Return whether this kind of boss still has a barrier in front of it.

    A boss is walled in by its own barrier alone: it has no shot out past that
    one line and does not leave the place it spawned in until it has come down,
    whatever the other bosses' barriers are doing.
    """
    return any(barrier[2] == boss_character for barrier in state.enemy_boss_barriers)
