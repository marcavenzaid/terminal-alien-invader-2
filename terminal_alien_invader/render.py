"""Drawing the world and the left display to the terminal."""
from terminal_alien_invader.config import (
    COLORS,
    DISPLAY_BORDER,
    ENEMY_RED_BOSS,
    ENEMY_RED_BOSS_FRENZY_MODE_SHIP,
    HEART,
    LEFT_DISPLAY_START_X,
    LEFT_DISPLAY_WIDTH,
    PLAYER_HEALTH_MAX,
    XCELLS,
    YCELLS,
)
from terminal_alien_invader.console import draw_at, erase_at
from terminal_alien_invader.state import state


def render_world():
    """Render the entire game world, including the player's ship, enemy ships, projectiles, and the left display."""
    for x in range(XCELLS):
        for y in range(YCELLS):
            cell_content = state.world[x][y]

            # The red boss in a frenzy is drawn in whichever of the frenzy's colours it has got to, but only on screen. 
            # Its cell goes on holding ENEMY_RED_BOSS, which is what everything else knows it by. 
            # Written into the world, a frenzied red boss would not be recognised as a ship at all.
            if cell_content == ENEMY_RED_BOSS and state.enemy_red_boss_in_frenzy_mode():
                cell_content = ENEMY_RED_BOSS_FRENZY_MODE_SHIP[state.enemy_red_boss_frenzy_mode_color_index]

            if cell_content:
                draw_at(x, y, cell_content)
            else:
                erase_at(x, y, 1)  # Clear empty cells

    render_left_display()


def render_left_display():
    """Render the left display area."""
    for y in range(YCELLS):
        state.world[LEFT_DISPLAY_WIDTH - 1][y] = DISPLAY_BORDER

    score_text = f"Score: {state.score}"
    # ljust measures the characters it is handed, so the bar is padded while it
    # is still plain text: color escapes in the string would be counted as width
    # the hearts do not take up on screen. The padding is what overwrites the
    # hearts the player has just lost with blanks instead of leaving them standing.
    for i, char in enumerate(score_text):
        state.world[LEFT_DISPLAY_START_X + 1 + i][1] = char

    move_instructions = f"Move: [←] [→] or [A] [D]"
    for i, char in enumerate(move_instructions):
        state.world[LEFT_DISPLAY_START_X + 1 + i][11] = char

    exit_instructions = f"Exit: [esc]"
    for i, char in enumerate(exit_instructions):
        state.world[LEFT_DISPLAY_START_X + 1 + i][13] = char

    # Each cell carries its own color escapes. draw_at puts a cursor move in
    # front of every cell it draws, so a cell holding one piece of a sequence
    # would have that sequence cut apart and the remainder printed as text.
    player_health_text = f"{HEART * state.player_health}".ljust(PLAYER_HEALTH_MAX + 2)
    for i, char in enumerate(player_health_text):
        state.world[LEFT_DISPLAY_START_X + 1 + i][YCELLS - 2] = f"{COLORS.RED}{char}{COLORS.RESET}"
