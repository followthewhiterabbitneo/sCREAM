"""Windows backend implementation: pynput + pyperclip + pystray.

- HotkeyListener: pynput keyboard listener on Caps Lock (toggle)
- Paster:         pyperclip + Ctrl+V simulation via pynput
- Tray:           pystray with PIL-generated icon and language submenu
"""

import ctypes
import threading
import time
from collections.abc import Callable

import pyperclip
import pystray
from PIL import Image, ImageDraw, ImageFont
from pynput import keyboard

from ..config import CLIPBOARD_RESTORE_DELAY


# ── Hotkey ───────────────────────────────────────────────────────────────────
class HotkeyListener:
    """Caps Lock toggle via pynput.

    1st tap: start recording.  2nd tap: stop recording.
    Uses GetKeyState to track the Caps Lock LED state, mirroring the macOS
    AlphaShift approach.
    """

    def __init__(self):
        self._caps_was_on = bool(ctypes.windll.user32.GetKeyState(0x14) & 1)
        self._on_toggle: Callable[[], None] | None = None

    def start(self, on_toggle: Callable[[], None]) -> None:
        self._on_toggle = on_toggle

        def _on_press(key: keyboard.Key | keyboard.KeyCode) -> None:
            if key != keyboard.Key.caps_lock:
                return
            caps_on = bool(ctypes.windll.user32.GetKeyState(0x14) & 1)
            if caps_on != self._caps_was_on and self._on_toggle:
                self._on_toggle()
            self._caps_was_on = caps_on

        print("\u2705 Hotkey listener started (Caps Lock)")
        with keyboard.Listener(on_press=_on_press) as listener:
            listener.join()


# ── Paste ────────────────────────────────────────────────────────────────────
class Paster:
    """Pastes via clipboard + Ctrl+V, restoring the previous clipboard contents."""

    _kb = keyboard.Controller()

    def paste_text(self, text: str) -> None:
        try:
            saved = pyperclip.paste()
        except pyperclip.PyperclipException:
            saved = ""

        pyperclip.copy(text)
        time.sleep(0.05)
        self._press_ctrl_v()

        time.sleep(CLIPBOARD_RESTORE_DELAY)
        try:
            pyperclip.copy(saved)
        except Exception as e:
            print(f"\u26a0\ufe0f failed to restore clipboard: {e}")

    def _press_ctrl_v(self) -> None:
        self._kb.press(keyboard.Key.ctrl)
        self._kb.press("v")
        self._kb.release("v")
        self._kb.release(keyboard.Key.ctrl)


# ── Tray ─────────────────────────────────────────────────────────────────────
def _make_icon_image(text: str = "\U0001f399", size: int = 64) -> Image.Image:
    """Render a small text/emoji icon as a PIL Image for pystray."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("segoe ui emoji", size - 16)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - w) / 2, (size - h) / 2), text, font=font, fill="white")
    return img


class Tray:
    """System-tray icon via pystray. All modes live under the Languages submenu."""

    def __init__(
        self,
        modes: list[tuple[str, str]],
        current_mode: str,
        on_mode_select: Callable[[str], None],
    ):
        self._current = current_mode
        self._on_mode_select = on_mode_select
        self._modes = modes
        self._status_text = "Ready"
        self._title_text = "\U0001f399"
        self._icon: pystray.Icon | None = None
        self._lock = threading.Lock()

    def _build_menu(self) -> pystray.Menu:
        lang_items = []
        for code, label in self._modes:
            lang_items.append(
                pystray.MenuItem(
                    label,
                    self._make_callback(code),
                    checked=lambda item, c=code: c == self._current,
                )
            )
        return pystray.Menu(
            pystray.MenuItem(self._status_text, None, enabled=False),
            pystray.MenuItem("Hotkey: Caps Lock", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("\U0001f30d Languages", pystray.Menu(*lang_items)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", lambda icon, item: icon.stop()),
        )

    def _make_callback(self, code: str):
        def _cb(icon: pystray.Icon, item: pystray.MenuItem) -> None:
            self.set_current_mode(code)
            self._on_mode_select(code)

        return _cb

    def _update_menu(self) -> None:
        if self._icon:
            self._icon.menu = self._build_menu()
            self._icon.update_menu()

    def set_title(self, title: str) -> None:
        with self._lock:
            self._title_text = title
            if self._icon:
                self._icon.icon = _make_icon_image(title)

    def set_status(self, text: str) -> None:
        with self._lock:
            self._status_text = text
            self._update_menu()

    def set_current_mode(self, code: str) -> None:
        with self._lock:
            self._current = code
            self._update_menu()

    def run(self) -> None:
        self._icon = pystray.Icon(
            "cream-typer",
            icon=_make_icon_image(self._title_text),
            title="Cream Typer",
            menu=self._build_menu(),
        )
        self._icon.run()
