"""The game loop and the life of a round: forming it up, playing it frame by frame, and closing it."""
import sys
import time

from terminal_alien_invader_2.config import (
    COLORS,
    FRAMES_PER_SECOND,
    GAME_OVER,
    MAIN_DISPLAY_START_X,
    MAIN_DISPLAY_WIDTH,
    ROUND_END_DURATION,
    YCELLS,
    YOU_WIN,
)
from terminal_alien_invader_2.collision import collision_detection
from terminal_alien_invader_2.console import open_new_console, restore_console
from terminal_alien_invader_2.controls import discard_keys, player_control
from terminal_alien_invader_2.effects import clear_finished_explosions
from terminal_alien_invader_2.enemies.attack import enemy_auto_attack, move_enemy_projectiles
from terminal_alien_invader_2.enemies.bosses import move_enemy_bosses, update_boss_barriers
from terminal_alien_invader_2.enemies.ranks import move_enemy_ranks, spawn_enemy
from terminal_alien_invader_2.enemies.red_boss import (
    change_enemy_red_boss_direction,
    teleport_enemy_red_boss,
    update_enemy_red_boss_frenzy_mode,
    update_enemy_red_boss_move_interval,
)
from terminal_alien_invader_2.player import move_player_projectiles, player_auto_attack, spawn_player
from terminal_alien_invader_2.render import render_world
from terminal_alien_invader_2.state import state


def main():
    # This condition prevents the game from rendering in the original terminal window if you are in an IDE.
    if open_new_console():
        return

    try:
        playing = True
        while playing:
            start_round()

            # The end of the round is looked for before anything else is done with the frame. 
            # Nothing may steer, fire or march after the frame the ship or the last of the bosses blew up on, 
            # or the world the round is closed over would no longer be the one it ended on.
            while round_result() is None and player_control():
                update()
                time.sleep(FRAMES_PER_SECOND)

            playing = end_round()
    finally:
        restore_console()


def update():
    """This function is called every frame to update the game state and render the game."""
    player_auto_attack()
    update_enemy_red_boss_frenzy_mode()
    enemy_auto_attack()
    move_player_projectiles()
    move_enemy_projectiles()
    move_enemy_ranks()

    # The red boss's pace, its teleports and its turns in a frenzy are all brought up to date before the bosses step,
    # so a jump due this frame is made from where the boss stood rather than from the cell one step along,
    # and the step due this frame is taken the new way.
    update_enemy_red_boss_move_interval()
    teleport_enemy_red_boss()
    change_enemy_red_boss_direction()
    move_enemy_bosses()
    clear_finished_explosions()
    update_boss_barriers()
    collision_detection()

    render_world()

    # Flush the output buffer to ensure that all drawing commands are sent to the terminal.
    sys.stdout.flush()


def start_round():
    """Clear away the round just played and form up a fresh one.

    Everything a round is played with is put back as it stood at the start of the game 
    (see GameState.reset), and the ship and the army are formed up on the wiped world.
    """
    state.reset()

    spawn_player()
    spawn_enemy()


def round_result():
    """What has become of the round, or None while it is still being played.

    GAME_OVER once the player's ship has been destroyed, YOU_WIN once the last
    of the bosses has been, and None for as long as the ship and some part of
    the army are both still standing. A ship destroyed on the very frame the
    last boss was still loses the round, since it is the wreck of it that the
    player is left looking at.
    """
    if state.player_destroyed:
        return GAME_OVER
    if state.boss_count == 0:
        return YOU_WIN
    return None


def end_round():
    """Close the round just played, and say whether another one follows.

    A round is closed with what became of it, put up in the middle of the main
    display over the world its last frame left. 
    GAME OVER over the wreck of the player's ship, 
    YOU WIN over the wreck of the last boss. 
    Nothing is touched while that text is up beyond the text itself, 
    so what stands on screen is the frame the round ended on. 
    Keys are read and thrown away as the pause is waited out, 
    so that the next round is not started with a backlog of them,
    and Esc still ends the game.

    Returns True once the pause has been waited out and the next round is to be
    played, and False if the player quit: out of the round itself, which leaves
    nothing to close and is not paused over at all, or out of the pause.
    """
    result = round_result()
    if result is None:
        return False

    text, colour = result

    # The text is centred on the main display, in whose own cells it is measured, 
    # so it sits in the middle of the play area rather than of the screen, which the left display takes a stretch of.
    text_x = MAIN_DISPLAY_START_X + (MAIN_DISPLAY_WIDTH - len(text)) // 2
    text_y = YCELLS // 2
    for i, character in enumerate(text):
        # Each cell carries its own colour escapes, as the left display's do.
        # draw_at puts a cursor move in front of every cell it draws, 
        # so a cell holding one piece of a sequence would have it cut apart.
        state.world[text_x + i][text_y] = f"{colour}{character}{COLORS.RESET}"

    # The one render of the pause, which puts the text up over the world the round left behind. 
    # Nothing is rendered again until the next round runs.
    render_world()
    sys.stdout.flush()

    end_time = time.monotonic() + ROUND_END_DURATION
    while time.monotonic() < end_time:
        if not discard_keys():
            return False
        time.sleep(FRAMES_PER_SECOND)
    return True
