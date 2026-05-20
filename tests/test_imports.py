"""Smoke test that the whole package imports cleanly (per-platform).

A failure here usually means a broken relative import after a refactor.
"""

import sys

import pytest


def test_package_imports():
    import cream_typer

    assert hasattr(cream_typer, "__version__")
    assert isinstance(cream_typer.__version__, str)


def test_config_imports():
    from cream_typer import config

    assert hasattr(config, "MODES")
    assert hasattr(config, "MENU_MODES")


def test_transcriber_imports():
    from cream_typer.transcriber import is_alive, transcribe  # noqa: F401


def test_recorder_imports():
    from cream_typer.recorder import AudioRecorder  # noqa: F401


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS-only backend")
def test_macos_backend_imports():
    from cream_typer.backend import HotkeyListener, Paster, Tray  # noqa: F401


@pytest.mark.skipif(sys.platform != "darwin", reason="app.py pulls in the macOS backend")
def test_app_imports():
    from cream_typer.app import VoiceTyper, main  # noqa: F401
