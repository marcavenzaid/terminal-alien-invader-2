"""Everything that changes while a round is played, kept on a single GameState.

Every module reads and writes the one shared instance, `state`, rather than
module-level globals: a `global` statement only reaches the module it is
written in, so state split across modules that way would drift apart.
"""
import time

from terminal_alien_invader.config import (
    ENEMY_RED_BOSS_MOVE_INTERVAL_RANGE,
    ENEMY_RANKS_NUMBER_ROWS,
    PLAYER_HEALTH_MAX,
    PLAYER_STARTING_X,
    PLAYER_STARTING_Y,
    XCELLS,
    YCELLS,
)


class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        """Put everything a round is played with back as it stood at the start of the game.

        The world is wiped rather than drawn over, so that none of the last round's ships, wreckage or
        GAME OVER is left standing in a cell the new round happens never to draw in.
        """
        # The game world is represented as a 2D list of characters,
        # where each cell can hold a character representing the player's ship, enemy ships, projectiles, or empty space.
        # The world is initialized with empty spaces with a size of XCELLS x YCELLS.
        self.world = [[' ' for _ in range(YCELLS)] for _ in range(XCELLS)]

        self.score = 0

        # ================================================================================
        # Controls
        # ================================================================================
        # Steering keys currently held down. A key is only added once its character has
        # come through the console, which is what proves this window had focus when it
        # was pressed, and is dropped as soon as the keyboard reports it released.
        # Keys held through the end of the last round are forgotten, so that the new
        # ship is only steered by one the player is still holding.
        # Such a key comes back the moment its character next reaches the console.
        self.held_movement_keys = set()

        # ================================================================================
        # Player
        # ================================================================================
        self.player_health = PLAYER_HEALTH_MAX

        self.player_x = PLAYER_STARTING_X
        self.player_y = PLAYER_STARTING_Y

        # Each projectile is a mutable [x, y] pair in screen-space, so it can be moved in place.
        self.player_projectiles = []
        self.player_last_attack = 0.0

        self.player_destroyed = False

        # This list holds the cells currently showing an explosion,
        # as a mutable [x, y, clear_time, character] record in screen-space,
        # so each one can be erased once its time is up.
        # The character is the mark the destroyed ship left, which differs by kind of ship, the player's own included.
        # The burst a shot of the player's leaves in front of the ship or barrier it strikes is recorded here as well
        # (see show_player_projectile_explosion_effect).
        self.explosions = []

        # ================================================================================
        # Enemy
        # ================================================================================
        # Which way each row of the ranks is travelling (1 for right, -1 for left),
        # one entry per row, in the order the rows were formed up in.
        # Neighbouring rows are sent opposite ways, the first of them to the left,
        # so the army sweeps back and forth through itself rather than sliding about as a single block.
        self.enemy_ranks_directions = [-1 if row % 2 == 0 else 1 for row in range(ENEMY_RANKS_NUMBER_ROWS)]

        # How far each row has been carried from where it formed up.
        # A row is moved in one piece, so a single offset places every ship in it.
        self.enemy_ranks_offsets = [0] * ENEMY_RANKS_NUMBER_ROWS

        # When the ranks are next due to take a step.
        # The rows share the one countdown, so they stay in time with one another however far each has got.
        # Zero means at once, so the army is already on the march on the frame it spawns.
        self.enemy_ranks_next_move = 0.0

        # How many ships of the ranks are still standing.
        # Everything the army is made of apart from the bosses counts here,
        # so this falling to zero is what says the ranks are gone and the bosses have nothing left to shelter behind.
        # The counts start at zero and are added to as spawn_enemy and spawn_bosses form the army up,
        # so that a round is never taken for won on the frames before the army it is played against has formed up.
        self.non_boss_enemy_count = 0

        # How many bosses are still standing.
        # They are the last of the army to be reached, sheltered behind the ranks and their barriers until the ranks are gone,
        # so this falling to zero is what says the whole army is beaten and the round is won.
        self.boss_count = 0

        # How many of the lesser bosses are still standing.
        # They are what holds the last boss's barrier up once the ranks are gone,
        # so this falling to zero is what says the last boss has nothing left to shelter behind either.
        self.lesser_boss_count = 0

        # Where each boss's barrier stands, as a [x, y, boss_character] record.
        # The x and y of its leftmost cell, and the boss it shelters.
        # Recorded when the bosses are placed, so each line can be redrawn every frame and taken down on its own
        # once whatever was holding it up is gone.
        # A boss with no record left here is one whose barrier is already down, which is what keeps a line from being taken down twice.
        self.enemy_boss_barriers = []

        # Each boss, as a mutable [x, y, direction, min_x, max_x, character, next_move] record in screen-space, so it can be moved in place.
        # min_x and max_x are the ends of the stretch of the row the boss marches, which it is never carried out of.
        # The zone of its own it spawned in for the lesser bosses, so the two of them never cross,
        # and the whole main display for the last boss, which is left alone on the row by the time it moves at all.
        # The row is kept here rather than taken for the bosses' own, because the red boss is
        # teleported off that row and goes on marching from whichever one it lands on (see teleport_enemy_red_boss).
        # The other two never leave the row they spawned on.
        # The character is what the boss is drawn with,
        # which is also what tells whether it is still standing where the record has it,
        # and which of the kinds' move intervals paces it.
        # next_move is when this boss is next due to take a step.
        # Each keeps its own countdown rather than sharing one as the ranks' rows do,
        # since the kinds march at different speeds.
        # Zero means at once, and it stays there for as long as a boss's own barrier keeps it standing still,
        # so each sets off the moment the line in front of it comes down.
        self.enemy_bosses = []

        # The red boss comes to each round with no pace drawn yet: the first pace it marches at is drawn as it sets off,
        # rather than being whichever one the last round happened to leave it holding.
        self.enemy_red_boss_move_interval = ENEMY_RED_BOSS_MOVE_INTERVAL_RANGE[1]
        self.enemy_red_boss_move_interval_next_change = 0.0

        # The red boss is owed no jump yet either. It is armed while that boss shelters,
        # so this is written over on the first frame of the round.
        self.enemy_red_boss_next_teleport = 0.0

        # Nor does it come to a round in a frenzy, or owed one.
        # The wait for the next is armed while the red boss shelters, as the wait for its next jump is.
        self.enemy_red_boss_next_frenzy_mode = 0.0
        self.enemy_red_boss_frenzy_mode_end = 0.0

        self.enemy_red_boss_frenzy_mode_color_index = 0

        self.enemy_red_boss_next_direction_change = 0.0

        # When each ship of the army is next due to fire, keyed by the cell it stands in.
        # The countdown belongs to the ship and marches along with it,
        # so a ship keeps to the rate of fire its kind was given however far it travels.
        # Only the front ship of a column has a clear shot, so only a ship that has reached the front is given a countdown,
        # and it waits out a full interval once it has.
        self.enemy_next_attack = {}

        # What each ship of the army has left of its health, keyed by the cell it stands in.
        # The health belongs to the ship and marches along with it exactly as its countdown does,
        # so a ship carries the damage it has taken wherever it goes.
        # A ship is entered here with its kind's full health as it spawns and taken out again once it is destroyed,
        # so an entry is only ever a standing ship's.
        self.enemy_health = {}

        # Each projectile is a mutable [x, y, character, damage] record in screen-space, so it can be moved in place.
        # It carries the shot of the kind of ship that fired it,
        # so it still knows what it looks like and what it takes off the player once it has left the ship behind.
        self.enemy_projectiles = []

    def enemy_red_boss_in_frenzy_mode(self):
        """Return whether the red boss is in a frenzy at this instant.

        A frenzy wears off on its own once its time is up, so it is read off the
        clock rather than kept as a flag that something would have to remember to clear.

        It lives here rather than with the rest of the red boss in enemies/red_boss.py because
        the attack, movement and rendering code all ask it, and red_boss.py depends on them.
        """
        return time.monotonic() < self.enemy_red_boss_frenzy_mode_end


# The one game state every module shares.
state = GameState()
