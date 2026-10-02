"""The console window the game is drawn in, and the escape sequences it is drawn with."""
import ctypes
import os
import subprocess
import sys

from terminal_alien_invader.config import XCELLS, YCELLS

# The folder the terminal_alien_invader package sits in.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def draw_at(x, y, text):
    """Write text with its first character at screen column x, row y (both 0-based).

    Only the cells the text covers are touched. 
    Everything else on screen is left as it was. 
    Nothing reaches the terminal until stdout is flushed.
    """
    sys.stdout.write(f"\x1b[{y + 1};{x + 1}H{text}")


def erase_at(x, y, length):
    """Erase length cells starting at screen column x, row y (both 0-based).

    Only the cells the text covers are touched. 
    Everything else on screen is left as it was. 
    Nothing reaches the terminal until stdout is flushed.
    """
    sys.stdout.write(f"\x1b[{y + 1};{x + 1}H{' ' * length}")


def open_new_console():
    """Relaunch the game in a new console window on Windows.

    Returns True in the original (parent) process so the caller can bail out
    instead of also rendering into the terminal it was launched from.
    """
    if os.environ.get("NEW_CONSOLE") != "1":
        env = os.environ.copy()
        env["NEW_CONSOLE"] = "1"

        # The game is relaunched as the terminal_alien_invader package, from the folder that holds it, 
        # so it starts the same way whether it was run with `python main.py` or `python -m terminal_alien_invader`.
        subprocess.Popen(
            [sys.executable, "-m", "terminal_alien_invader"],
            cwd=PROJECT_ROOT,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            env=env
        )
        return True

    # Resize the console window to the desired size
    def _resize_console(cols, rows):
        """Resize the terminal window. Replaces `mode con:`, which Windows Terminal ignores."""
        if os.name == "nt":
            k = ctypes.windll.kernel32
            # 7 = PROCESSED_OUTPUT | WRAP_AT_EOL | VIRTUAL_TERMINAL_PROCESSING
            k.SetConsoleMode(k.GetStdHandle(-11), 7)
        # ?1049h switches to the alternate screen buffer. It is always exactly
        # the size of the viewport and keeps no scrollback, so there is nothing
        # to scroll and no scrollbar appears.
        print("\x1b[?1049h", end="", flush=True)
        print(f"\x1b[8;{rows};{cols}t", end="", flush=True)
        # ?25l hides the cursor so it does not blink on top of the rendered cells.
        print("\x1b[?25l", end="", flush=True)
    
    _resize_console(XCELLS, YCELLS)
    return False


def restore_console():
    """Leave the alternate screen buffer, restoring what the terminal showed before.
    This is called when the game exits, so the user sees their original terminal content.
    """
    print("\x1b[?25h\x1b[?1049l", end="", flush=True)
