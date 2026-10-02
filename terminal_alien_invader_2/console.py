"""The console window the game is drawn in, and the escape sequences it is drawn with."""
import ctypes
import os
import subprocess
import sys

from terminal_alien_invader_2.config import XCELLS, YCELLS

# The folder the terminal_alien_invader_2 package sits in.
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


def _process_image_path(pid):
    """Return the full path of the program a process is running, or None if Windows will not say."""
    k = ctypes.windll.kernel32
    k.OpenProcess.restype = ctypes.c_void_p
    k.QueryFullProcessImageNameW.argtypes = [
        ctypes.c_void_p, ctypes.c_uint32, ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_uint32)
    ]
    k.CloseHandle.argtypes = [ctypes.c_void_p]

    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    handle = k.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return None
    try:
        size = ctypes.c_uint32(32768)
        buffer = ctypes.create_unicode_buffer(size.value)
        if not k.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
            return None
        return buffer.value
    finally:
        k.CloseHandle(handle)


def console_is_own():
    """Report whether nothing but this game is attached to the console it is running in.

    True when the console was made just for the game, e.g. when the exe is double-clicked.
    False when it is shared with a shell, as in an IDE's built-in terminal or a command prompt.
    Every process running the same program as this one counts as the game, since a
    one-file PyInstaller exe runs as a small launcher plus the game itself.
    """
    pids = (ctypes.c_uint32 * 64)()
    count = ctypes.windll.kernel32.GetConsoleProcessList(pids, len(pids))
    if not 0 < count <= len(pids):
        return False

    for pid in pids[:count]:
        if pid == os.getpid():
            continue
        path = _process_image_path(pid)
        try:
            if path is None or not os.path.samefile(path, sys.executable):
                return False
        except OSError:
            return False
    return True


def open_new_console():
    """Relaunch the game in a new console window on Windows, unless its console is already its own.

    Returns True in the original (parent) process so the caller can bail out
    instead of also rendering into the terminal it was launched from.
    """
    # A console shared with a shell cannot be relied on to take the game's size (an IDE's terminal
    # is sized by the IDE), so the game moves to a console of its own. NEW_CONSOLE marks the relaunched
    # copy, so it never relaunches again.
    if os.environ.get("NEW_CONSOLE") != "1" and not console_is_own():
        env = os.environ.copy()
        env["NEW_CONSOLE"] = "1"

        # The game is relaunched as the terminal_alien_invader_2 package, from the folder that holds it,
        # so it starts the same way whether it was run with `python main.py` or `python -m terminal_alien_invader_2`.
        # A PyInstaller exe sets sys.frozen, and its sys.executable is the exe itself, so it is just run again.
        # PYINSTALLER_RESET_ENVIRONMENT makes the new copy unpack itself instead of reusing this copy's
        # temporary folder, which is deleted as soon as this copy exits.
        if getattr(sys, "frozen", False):
            env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
            cmd = [sys.executable]
        else:
            cmd = [sys.executable, "-m", "terminal_alien_invader_2"]
        subprocess.Popen(
            cmd,
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
