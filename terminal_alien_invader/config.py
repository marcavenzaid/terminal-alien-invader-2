"""Every fixed setting of the game: colours, display sizes, timings, and what each kind of ship looks like and does.

Nothing in here changes while the game runs. What does lives in state.py.
"""


class COLORS:
    """ANSI color codes"""
    RESET = "\x1b[0m"
    WHITE = "\x1b[37m"
    WHITE_BRIGHT = "\x1b[97m"
    GRAY = "\x1b[90m"
    RED = "\x1b[31m"
    RED_BRIGHT = "\x1b[91m"
    ORANGE = "\x1b[38;5;208m"
    ORANGE_BRIGHT = "\x1b[38;5;214m"
    YELLOW = "\x1b[33m"
    YELLOW_BRIGHT = "\x1b[93m"
    YELLOW_GREEN = "\x1b[38;5;148m"
    YELLOW_GREEN_BRIGHT = "\x1b[38;5;154m"
    GREEN = "\x1b[32m"
    GREEN_BRIGHT = "\x1b[92m"
    CYAN = "\x1b[36m"
    CYAN_BRIGHT = "\x1b[96m"
    BLUE = "\x1b[34m"
    BLUE_BRIGHT = "\x1b[94m"
    VIOLET = "\x1b[38;5;93m"
    VIOLET_BRIGHT = "\x1b[38;5;135m"
    MAGENTA = "\x1b[35m"
    MAGENTA_BRIGHT = "\x1b[95m"

# ================================================================================
# UI and Settings
# ================================================================================
FRAMES_PER_SECOND = 1 / 20

LEFT_DISPLAY_WIDTH = 30
MAIN_DISPLAY_WIDTH = 80

LEFT_DISPLAY_START_X = 0
MAIN_DISPLAY_START_X = LEFT_DISPLAY_WIDTH

DISPLAY_BORDER = "│" # │ ║

XCELLS = LEFT_DISPLAY_WIDTH + MAIN_DISPLAY_WIDTH
YCELLS = 30

HEART = "♥" # ♥ █

GAME_OVER = ("GAME OVER", COLORS.RESET)
YOU_WIN = ("YOU WIN", COLORS.RESET)

ROUND_END_DURATION = 5.0  # How long the world is left frozen under that text before the next round forms up, in seconds.

# ================================================================================
# Controls
# ================================================================================
# Arrow keys have no character of their own, so they arrive as two reads:
# one of these prefixes, then a scan code that getwch() hands back as a letter.
ARROW_PREFIXES = ("\x00", "\xe0")
KEY_LEFT = "K"   # Left arrow, scan code 0x4B.
KEY_RIGHT = "M"  # Right arrow, scan code 0x4D.
KEY_ESCAPE = "\x1b"

# Virtual-key codes for the keys that steer the ship, paired with the direction each one sends it. 
# Windows pauses before it starts repeating a held key, so the ship is moved by asking the keyboard 
# which of these is down (see move_held_keys) rather than by counting the characters the console repeats.
VK_LEFT = 0x25
VK_RIGHT = 0x27
VK_A = 0x41
VK_D = 0x44
MOVEMENT_DIRECTIONS = {VK_LEFT: -1, VK_A: -1, VK_RIGHT: 1, VK_D: 1}

# ================================================================================
# Player
# ================================================================================
PLAYER_SHIP = f"{COLORS.WHITE_BRIGHT}Ѧ{COLORS.RESET}" # ╧ ┴ ♗ ♝ ۩

PLAYER_SHIP_EXPLOSION = f"{COLORS.WHITE_BRIGHT}☠{COLORS.RESET}"

# The color escapes take up no room on screen, and every cell is drawn at its
# own absolute position, so the shot still covers exactly one column.
PLAYER_PROJECTILE = f"{COLORS.CYAN_BRIGHT}'{COLORS.RESET}"

PLAYER_HEALTH_MAX = 26

PLAYER_PROJECTILE_DAMAGE = 1

PLAYER_PROJECTILE_EXPLOSION_EFFECT = f"{COLORS.CYAN_BRIGHT}*{COLORS.RESET}"

# How long the burst a shot leaves in front of the ship or barrier it strikes stays on screen, in seconds.
PLAYER_PROJECTILE_EXPLOSION_EFFECT_DURATION = 0.1

PLAYER_STARTING_X = (MAIN_DISPLAY_WIDTH // 2) + MAIN_DISPLAY_START_X
PLAYER_STARTING_Y = YCELLS - 5

# The ship may sit on any column of the main display.
PLAYER_MIN_X = MAIN_DISPLAY_START_X
PLAYER_MAX_X = XCELLS - 1

# How many cells either side of the ship's own count as part of it when a shot is checked against it. 
# The ship is drawn in a single cell, but it is taken to be wider than the glyph standing for it: 
# at 1 it is three cells across, its own and the one to each side, 
# At 0 the hitbox is the drawn cell and nothing more.
PLAYER_HITBOX_RADIUS = 1

PLAYER_ATTACK_INTERVAL = 0.15  # The ship fires on its own. This is the cooldown between shots, in seconds.

EXPLOSION_DURATION = 0.4  # How long the mark left by a destroyed ship stays on screen, in seconds.

# ================================================================================
# Enemy
# ================================================================================
ENEMY_1 = "☨" # ¥ ☨
ENEMY_RED_BOSS = f"{COLORS.RED}༒{COLORS.RESET}"
ENEMY_ORANGE_BOSS = f"{COLORS.ORANGE}Ӝ{COLORS.RESET}"
ENEMY_GREEN_BOSS = f"{COLORS.GREEN_BRIGHT}☬{COLORS.RESET}"

ENEMY_1_MAX_HEALTH = 1
ENEMY_RED_BOSS_MAX_HEALTH = 40
ENEMY_ORANGE_BOSS_MAX_HEALTH = 10
ENEMY_GREEN_BOSS_MAX_HEALTH = 10

# How many cells either side of a boss's own count as part of it when a shot is checked against it, 
# exactly as PLAYER_HITBOX_RADIUS does for the ship: 
# at 1 a boss is three cells across, its own and the one to each side, 
# At 0 the hitbox is the drawn cell and nothing more.
ENEMY_BOSS_HITBOX_RADIUS = 1

ENEMY_1_PROJECTILE = f"{COLORS.RESET}∙{COLORS.RESET}"
# The red boss's bolt comes in the one colour, except in frenzy mode (see ENEMY_RED_BOSS_FRENZY_MODE_PROJECTILE).
ENEMY_RED_BOSS_PROJECTILE = (f"{COLORS.RED}│{COLORS.RESET}")
ENEMY_ORANGE_BOSS_PROJECTILE = ( 
    f"{COLORS.YELLOW_BRIGHT}☤{COLORS.RESET}",
    f"{COLORS.YELLOW_BRIGHT}Ö{COLORS.RESET}")
ENEMY_GREEN_BOSS_PROJECTILE = (
    f"{COLORS.GREEN_BRIGHT}.{COLORS.RESET}", 
    f"{COLORS.GREEN_BRIGHT}•{COLORS.RESET}", 
    f"{COLORS.GREEN_BRIGHT}°{COLORS.RESET}", 
    f"{COLORS.GREEN_BRIGHT}○{COLORS.RESET}")

ENEMY_1_EXPLOSION = f"{COLORS.RED}¤{COLORS.RESET}"
ENEMY_RED_BOSS_EXPLOSION = f"{COLORS.RED}☠{COLORS.RESET}" 
ENEMY_ORANGE_BOSS_EXPLOSION = f"{COLORS.ORANGE}☠{COLORS.RESET}" 
ENEMY_GREEN_BOSS_EXPLOSION = f"{COLORS.GREEN_BRIGHT}☠{COLORS.RESET}" 

# Every so often the red boss goes into a frenzy. 
# For as long as it lasts, the boss teleports, moves and fires at the frenzy's pace, 
# and is drawn, along with every bolt it fires, in the colours of ENEMY_RED_BOSS_FRENZY_MODE_COLORS. 
# The boss cycles through them in the order they are listed, 
# The wait from the start of one of frenzy to the start of the next is ENEMY_RED_BOSS_FRENZY_MODE_INTERVAL_RANGE, 
# and lasts ENEMY_RED_BOSS_FRENZY_MODE_DURATION seconds..
ENEMY_RED_BOSS_FRENZY_MODE_INTERVAL_RANGE = (10, 15)
ENEMY_RED_BOSS_FRENZY_MODE_DURATION = 7
ENEMY_RED_BOSS_FRENZY_MODE_COLORS = (
    COLORS.RED,
    COLORS.ORANGE_BRIGHT,
    COLORS.YELLOW,
    COLORS.YELLOW_GREEN_BRIGHT,
    COLORS.GREEN_BRIGHT,
    COLORS.CYAN_BRIGHT,
    COLORS.BLUE_BRIGHT,
    COLORS.VIOLET_BRIGHT,
    COLORS.MAGENTA_BRIGHT,
)

ENEMY_RED_BOSS_FRENZY_MODE_SHIP = tuple(
    f"{color}༒{COLORS.RESET}" for color in ENEMY_RED_BOSS_FRENZY_MODE_COLORS
)
ENEMY_RED_BOSS_FRENZY_MODE_PROJECTILE = tuple(
    f"{color}│{COLORS.RESET}" for color in ENEMY_RED_BOSS_FRENZY_MODE_COLORS
)

ENEMY_RED_BOSS_FRENZY_MODE_TELEPORT_INTERVAL_RANGE = (0, 1)
ENEMY_RED_BOSS_FRENZY_MODE_MOVE_INTERVAL = 0
ENEMY_RED_BOSS_FRENZY_MODE_ATTACK_INTERVAL = 0

ENEMY_RED_BOSS_FRENZY_MODE_CHANGE_DIRECTION_INTERVAL = (0, 1.5)

ENEMY_1_ATTACK_INTERVAL_RANGE = (1, 4) 
ENEMY_RED_BOSS_ATTACK_INTERVAL_RANGE = (0, 0.1)  
ENEMY_ORANGE_BOSS_ATTACK_INTERVAL_RANGE = (0.2, 1)  
ENEMY_GREEN_BOSS_ATTACK_INTERVAL_RANGE = (0, 0.4) 

ENEMY_1_PROJECTILE_DAMAGE = 1
ENEMY_RED_BOSS_PROJECTILE_DAMAGE = 11
ENEMY_ORANGE_BOSS_PROJECTILE_DAMAGE = 5
ENEMY_GREEN_BOSS_PROJECTILE_DAMAGE = 1

# How long the ranks wait between one sideways step and the next, in seconds.
ENEMY_RANKS_MOVE_INTERVAL = 0.2

# How long a boss of each kind waits between one sideways step and the next, in seconds.
ENEMY_ORANGE_BOSS_MOVE_INTERVAL = 0.2
ENEMY_GREEN_BOSS_MOVE_INTERVAL = 0.15

ENEMY_RED_BOSS_MOVE_INTERVAL_RANGE = (0.1, 0.15)  # The wait between one sideways step and the next, in seconds.
ENEMY_RED_BOSS_MOVE_INTERVAL_CHANGE_INTERVAL = 3  # The wait before choosing a new value in ENEMY_RED_BOSS_MOVE_INTERVAL_RANGE.

ENEMY_RED_BOSS_TELEPORT_INTERVAL_RANGE = (0, 7)

# The wall a boss shelters behind while the ranks are still standing.
ENEMY_RED_BOSS_BARRIER_CHARACTER = f"{COLORS.RED}─{COLORS.RESET}"
ENEMY_ORANGE_BOSS_BARRIER_CHARACTER = f"{COLORS.ORANGE}─{COLORS.RESET}"
ENEMY_GREEN_BOSS_BARRIER_CHARACTER = f"{COLORS.GREEN_BRIGHT}─{COLORS.RESET}"
ENEMY_BOSS_BARRIER_WIDTH = 5

ENEMY_1_KILL_SCORE = 39
ENEMY_RED_BOSS_KILL_SCORE = 7777777
ENEMY_ORANGE_BOSS_KILL_SCORE = 55555
ENEMY_GREEN_BOSS_KILL_SCORE = 333333

# The kinds of ship the army is drawn from, and what each kind shoots and leaves behind when it is destroyed. 
# A ship is nothing but its character once it stands in the world, 
# so these are what turn the character in a cell back into the kind of ship standing there.
# The ranks are filled from ENEMY_RANK_CHARACTERS. 
# The bosses are placed one to a kind and so are kept apart. 
# ENEMY_CHARACTERS is everything that counts as an enemy ship, bosses included.
ENEMY_RANK_CHARACTERS = (ENEMY_1,)  # The trailing comma is what keeps one kind a tuple.
ENEMY_BOSS_CHARACTERS = (ENEMY_RED_BOSS, ENEMY_ORANGE_BOSS, ENEMY_GREEN_BOSS)
ENEMY_CHARACTERS = ENEMY_RANK_CHARACTERS + ENEMY_BOSS_CHARACTERS

# The bosses are fought in two waves rather than all three at once. 
# The lesser bosses are freed the moment the ranks are gone, as the whole line of them once was. 
# The last boss is held back behind a barrier of its own for that fight and
# freed only once both of them have been destroyed, to fight it alone. 
ENEMY_LAST_BOSS = ENEMY_RED_BOSS
ENEMY_LESSER_BOSSES = (ENEMY_ORANGE_BOSS, ENEMY_GREEN_BOSS)

ENEMY_PROJECTILES = {
    ENEMY_1: ENEMY_1_PROJECTILE,
    ENEMY_RED_BOSS: ENEMY_RED_BOSS_PROJECTILE,
    ENEMY_ORANGE_BOSS: ENEMY_ORANGE_BOSS_PROJECTILE,
    ENEMY_GREEN_BOSS: ENEMY_GREEN_BOSS_PROJECTILE,
}

ENEMY_EXPLOSIONS = {
    ENEMY_1: ENEMY_1_EXPLOSION,
    ENEMY_RED_BOSS: ENEMY_RED_BOSS_EXPLOSION,
    ENEMY_ORANGE_BOSS: ENEMY_ORANGE_BOSS_EXPLOSION,
    ENEMY_GREEN_BOSS: ENEMY_GREEN_BOSS_EXPLOSION,
}

ENEMY_BOSS_BARRIER_CHARACTERS = {
    ENEMY_RED_BOSS: ENEMY_RED_BOSS_BARRIER_CHARACTER,
    ENEMY_ORANGE_BOSS: ENEMY_ORANGE_BOSS_BARRIER_CHARACTER,
    ENEMY_GREEN_BOSS: ENEMY_GREEN_BOSS_BARRIER_CHARACTER,
}

ENEMY_MAX_HEALTHS = {
    ENEMY_1: ENEMY_1_MAX_HEALTH,
    ENEMY_RED_BOSS: ENEMY_RED_BOSS_MAX_HEALTH,
    ENEMY_ORANGE_BOSS: ENEMY_ORANGE_BOSS_MAX_HEALTH,
    ENEMY_GREEN_BOSS: ENEMY_GREEN_BOSS_MAX_HEALTH,
}

ENEMY_ATTACK_INTERVAL_RANGES = {
    ENEMY_1: ENEMY_1_ATTACK_INTERVAL_RANGE,
    ENEMY_RED_BOSS: ENEMY_RED_BOSS_ATTACK_INTERVAL_RANGE,
    ENEMY_ORANGE_BOSS: ENEMY_ORANGE_BOSS_ATTACK_INTERVAL_RANGE,
    ENEMY_GREEN_BOSS: ENEMY_GREEN_BOSS_ATTACK_INTERVAL_RANGE,
}

ENEMY_PROJECTILE_DAMAGES = {
    ENEMY_1: ENEMY_1_PROJECTILE_DAMAGE,
    ENEMY_RED_BOSS: ENEMY_RED_BOSS_PROJECTILE_DAMAGE,
    ENEMY_ORANGE_BOSS: ENEMY_ORANGE_BOSS_PROJECTILE_DAMAGE,
    ENEMY_GREEN_BOSS: ENEMY_GREEN_BOSS_PROJECTILE_DAMAGE,
}

ENEMY_KILL_SCORES = {
    ENEMY_1: ENEMY_1_KILL_SCORE,
    ENEMY_RED_BOSS: ENEMY_RED_BOSS_KILL_SCORE,
    ENEMY_ORANGE_BOSS: ENEMY_ORANGE_BOSS_KILL_SCORE,
    ENEMY_GREEN_BOSS: ENEMY_GREEN_BOSS_KILL_SCORE,
}

ENEMY_BOSS_MOVE_INTERVALS = {
    ENEMY_ORANGE_BOSS: ENEMY_ORANGE_BOSS_MOVE_INTERVAL,
    ENEMY_GREEN_BOSS: ENEMY_GREEN_BOSS_MOVE_INTERVAL,
}

ENEMY_STARTING_Y = 1
ENEMY_NUMBER_PER_ROW = 31
ENEMY_NUMBER_ROWS = 13

# The column the leftmost place in the army's grid is formed up on, 
# which puts the grid in the middle of the main display. 
# Each place takes two cells, the ship's own and the gap kept after it.
ENEMY_STARTING_X = MAIN_DISPLAY_START_X + ((MAIN_DISPLAY_WIDTH - ENEMY_NUMBER_PER_ROW * 2) // 2)

# The chance, from 0 to 1, that a place in the ranks drawn for an ENEMY_1 is actually filled by one. 
# A failed roll leaves that place empty, so the army forms up with gaps scattered through it rather than as a solid block.
ENEMY_1_SPAWN_CHANCE = 0.25

# Rows of clear space left between the bosses' row and the ranks in front of it,
# so the bosses read as a line of their own rather than as the army's back rank.
ENEMY_BOSS_ROW_GAP = 2

# The row the barriers stand on. 
# The first of the rows of clear space in front of the bosses, so a barrier sits directly in front of the boss it shelters.
ENEMY_BOSS_BARRIER_Y = ENEMY_STARTING_Y + 1

# The ranks' own rows. Every row of the grid but the back one, which is the bosses', 
# and they form up in front of the clear space left after it.
ENEMY_RANKS_NUMBER_ROWS = ENEMY_NUMBER_ROWS - 1
ENEMY_RANKS_STARTING_Y = ENEMY_STARTING_Y + 1 + ENEMY_BOSS_ROW_GAP

# The stretch of the display the army holds between them. 
# Rvery column of the main display, which is as far as any row of the ranks is ever carried, 
# and the rows from the bosses' own at the back down to the front rank. 
# It is the zone the red boss's teleports are drawn from (see teleport_enemy_red_boss), 
# so a jump only ever puts it where some ship of the army could have stood, 
# never down among the player's own rows or off an edge of the display.
ENEMY_ZONE_MIN_X = MAIN_DISPLAY_START_X
ENEMY_ZONE_MAX_X = XCELLS - 1
ENEMY_ZONE_MIN_Y = ENEMY_STARTING_Y
ENEMY_ZONE_MAX_Y = ENEMY_RANKS_STARTING_Y + ENEMY_RANKS_NUMBER_ROWS - 1

# How far a row may be carried from where it formed up before it has to turn around. 
# The limits are measured from the places at the ends of a row rather than from the ships standing in them, 
# so a row turns in the same two places all game however many of its ships are left and wherever the gaps in it fell.
# At the left, when the first place in the row is on the first column of the main display. 
# At the right, when the last place is on the last column.
ENEMY_RANKS_MIN_OFFSET = MAIN_DISPLAY_START_X - ENEMY_STARTING_X
ENEMY_RANKS_MAX_OFFSET = (XCELLS - 1) - (ENEMY_STARTING_X + (ENEMY_NUMBER_PER_ROW - 1) * 2)
