"""The ranks of ordinary enemy ships: forming the army up and marching its rows."""
import random
import time

from terminal_alien_invader.config import (
    ENEMY_1,
    ENEMY_1_SPAWN_CHANCE,
    ENEMY_MAX_HEALTHS,
    ENEMY_NUMBER_PER_ROW,
    ENEMY_RANKS_MAX_OFFSET,
    ENEMY_RANKS_MIN_OFFSET,
    ENEMY_RANKS_MOVE_INTERVAL,
    ENEMY_RANKS_NUMBER_ROWS,
    ENEMY_RANKS_STARTING_Y,
    ENEMY_RANK_CHARACTERS,
    ENEMY_STARTING_X,
    MAIN_DISPLAY_START_X,
    XCELLS,
)
from terminal_alien_invader.enemies.bosses import spawn_bosses
from terminal_alien_invader.state import state


def spawn_enemy():
    """Spawn an entire army of enemy ships at the top of the main display.

    Every ship in the ranks is one of the kinds in ENEMY_RANK_CHARACTERS, drawn
    at random, so the army is a mix of however many kinds are listed there. A
    kind with a spawn chance has to make its roll as well, so some of the places
    drawn for one are left empty and the ranks form up with gaps in them. The
    back row, the one furthest from the player, is left to the bosses, with
    ENEMY_BOSS_ROW_GAP rows of clear space between them and the ranks.

    Every ship the ranks are filled with is counted into non_boss_enemy_count,
    which is what the bosses' barriers stand on.
    """
    # The enemy ships are arranged in a grid, with ENEMY_NUMBER_PER_ROW ships per row
    # and ENEMY_NUMBER_ROWS rows, the back one being the bosses'. The grid is formed
    # up on ENEMY_STARTING_X, which centers it within the main display area.

    # The back row is the bosses' and the gap is left empty, so the ranks form up
    # in front of both, on the rows from ENEMY_RANKS_STARTING_Y onwards.
    for row in range(ENEMY_RANKS_NUMBER_ROWS):
        # Each row of enemy ships is drawn, with a horizontal spacing of 2 cells between ships.
        for col in range(0, ENEMY_NUMBER_PER_ROW * 2, 2):
            x = ENEMY_STARTING_X + col
            y = ENEMY_RANKS_STARTING_Y + row
            enemy = random.choice(ENEMY_RANK_CHARACTERS)

            # The ship drawn for this place still has to make its spawn roll to take it. 
            # A failed roll leaves the place empty.
            if enemy == ENEMY_1 and random.random() >= ENEMY_1_SPAWN_CHANCE:
                continue

            state.world[x][y] = enemy
            state.enemy_health[(x, y)] = ENEMY_MAX_HEALTHS[enemy]
            state.non_boss_enemy_count += 1

    spawn_bosses()


def move_enemy_ranks():
    """Step every row of the ranks one cell along the way it is travelling.

    Each row is carried in one piece, so it keeps the shape it formed up in, and
    neighbouring rows travel opposite ways: the first row of the ranks sets off
    to the left, the row behind it to the right, and so on back through the
    army, so it sweeps through itself rather than sliding about as one block.
    The rows share a countdown and so step together, which keeps them in time
    with one another however far each has got.

    Called every frame, but the steps themselves are paced by wall-clock time as
    everything else that moves on its own is, so the army crosses the display at
    the same speed whatever rate the loop runs at.

    Once the ranks are gone there is nothing left to carry.
    """
    if state.non_boss_enemy_count <= 0:
        return

    now = time.monotonic()
    if now < state.enemy_ranks_next_move:
        return

    state.enemy_ranks_next_move = now + ENEMY_RANKS_MOVE_INTERVAL

    for row in range(ENEMY_RANKS_NUMBER_ROWS):
        step_enemy_rank(row)


def step_enemy_rank(row):
    """Carry one row of the ranks a single cell the way it is travelling.

    A row marches on until the leading end of it has reached the edge of the
    main display. It takes that edge before it turns: having stepped onto it,
    the next step the row is due is the one back the other way.
    """
    next_offset = state.enemy_ranks_offsets[row] + state.enemy_ranks_directions[row]
    if not ENEMY_RANKS_MIN_OFFSET <= next_offset <= ENEMY_RANKS_MAX_OFFSET:
        # The row is standing on the edge it was marching towards, so this is
        # the step that sends it back the other way.
        state.enemy_ranks_directions[row] = -state.enemy_ranks_directions[row]
        next_offset = state.enemy_ranks_offsets[row] + state.enemy_ranks_directions[row]
        if not ENEMY_RANKS_MIN_OFFSET <= next_offset <= ENEMY_RANKS_MAX_OFFSET:
            # A grid as wide as the display it stands in has nowhere to march.
            return

    state.enemy_ranks_offsets[row] = next_offset
    shift_enemy_rank(ENEMY_RANKS_STARTING_Y + row, state.enemy_ranks_directions[row])


def shift_enemy_rank(y, dx):
    """Move every ship standing on row y of the world dx cells sideways.

    Every ship in the row is lifted out of the world before any of them is put
    back, so no ship is ever written into a cell another has yet to leave. Only
    the one row is touched, so the rows travelling the other way are left where
    they are.

    The countdowns of the ships on the row travel with them, and so does what
    each has left of its health, exactly as a boss's do (see step_enemy_boss).
    Left behind, they would be picked up by whichever ship marched into the
    column next, and a ship crossing a stretch of columns that had all come due
    would fire on nearly every step it took: five or six shots a second from one
    ship, and then nothing from it for as long as it took to reach the next
    stretch. Carried along, each ship keeps the interval its kind was given
    between one shot of its own and the next, and the damage it has taken.

    Called from the part of the frame where none of the projectiles is drawn in
    the world, so the ships are moved among empty cells, and a shot that a ship
    has just stepped in front of meets it there when the projectiles are checked
    against what they flew into.
    """
    ships = []
    for x in range(MAIN_DISPLAY_START_X, XCELLS):
        if state.world[x][y] in ENEMY_RANK_CHARACTERS:
            ships.append((x, state.world[x][y]))

    # Every countdown standing on the row is lifted out before any is put back,
    # so one ship's is never written into a cell another has yet to leave. What
    # the ships have left of their health is carried across the same way.
    carried = {}
    carried_health = {}
    for x, _ in ships:
        due = state.enemy_next_attack.pop((x, y), None)
        if due is not None:
            carried[(x + dx, y)] = due

        remaining = state.enemy_health.pop((x, y), None)
        if remaining is not None:
            carried_health[(x + dx, y)] = remaining

    for x, _ in ships:
        state.world[x][y] = ' '
    for x, enemy in ships:
        state.world[x + dx][y] = enemy

    # A countdown or a scrap of health still left in a cell a ship has just
    # stepped into belonged to a ship destroyed there, and is dropped rather
    # than handed on: picked up, it would have the ship firing on nearly every
    # step it took, or standing in for the health it had already spent.
    for x, _ in ships:
        state.enemy_next_attack.pop((x + dx, y), None)
        state.enemy_health.pop((x + dx, y), None)
    state.enemy_next_attack.update(carried)
    state.enemy_health.update(carried_health)
