"""Unit tests for the Windows backend — runs only on win32.

The hotkey listener, paster, and tray are exercised with mocked system
dependencies so the suite stays fast and doesn't require an active desktop.
"""

import sys

import pytest

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows-only backend")


def test_hotkey_listener_instantiates():
    from cream_typer.backend._windows import HotkeyListener

    listener = HotkeyListener()
    assert listener._on_toggle is None


def test_paster_instantiates():
    from cream_typer.backend._windows import Paster

    paster = Paster()
    assert hasattr(paster, "paste_text")


def test_tray_instantiates():
    from cream_typer.backend._windows import Tray

    tray = Tray(
        modes=[("en", "English"), ("ru", "Russian")],
        current_mode="en",
        on_mode_select=lambda code: None,
    )
    assert tray._current == "en"


def test_make_icon_image_returns_pil_image():
    from cream_typer.backend._windows import _make_icon_image

    img = _make_icon_image("T", size=32)
    assert img.size == (32, 32)
    assert img.mode == "RGBA"


def test_tray_set_status():
    from cream_typer.backend._windows import Tray

    tray = Tray(
        modes=[("en", "English")],
        current_mode="en",
        on_mode_select=lambda code: None,
    )
    tray.set_status("Recording...")
    assert tray._status_text == "Recording..."


def test_tray_set_current_mode():
    from cream_typer.backend._windows import Tray

    tray = Tray(
        modes=[("en", "English"), ("ru", "Russian")],
        current_mode="en",
        on_mode_select=lambda code: None,
    )
    tray.set_current_mode("ru")
    assert tray._current == "ru"
