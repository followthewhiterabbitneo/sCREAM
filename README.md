# sCREAM

**Voice translation in any direction. Locally on your machine.**

Fork of [cream-typer](https://github.com/adjacentai/cream-typer) with **Windows support**.

Tap Caps Lock, speak any language, get any other. Whisper.cpp, no cloud, no GPU rental.

---

## Platforms

| Platform | Backend | Status |
|---|---|---|
| macOS (Apple Silicon) | Quartz + rumps | Shipped |
| **Windows** | **pynput + pystray** | **Shipped** |
| Linux | pynput + pystray (X11) | TBD |

---

## Install (Windows)

Requires **Python 3.10+**, **Git**, and **CMake** (for building whisper.cpp).

### 1. Clone and install Python deps

```powershell
git clone https://github.com/followthewhiterabbitneo/sCREAM.git
cd sCREAM
python -m venv venv
.\venv\Scripts\activate
pip install -e ".[windows,dev]"
```

### 2. Build whisper.cpp

```powershell
git clone --depth 1 https://github.com/ggerganov/whisper.cpp.git vendor\whisper.cpp
cmake -B vendor\whisper.cpp\build -S vendor\whisper.cpp -DWHISPER_BUILD_SERVER=ON -DCMAKE_BUILD_TYPE=Release
cmake --build vendor\whisper.cpp\build --target whisper-server --config Release -j
```

### 3. Download the model (~550 MB)

```powershell
cd vendor\whisper.cpp
python -c "import urllib.request; urllib.request.urlretrieve('https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo-q5_0.bin', 'models/ggml-large-v3-turbo-q5_0.bin')"
cd ..\..
```

### 4. Run

In two terminals:

```powershell
# Terminal 1 — whisper server
.\scripts\whisper_server.ps1

# Terminal 2 — the app
python -m cream_typer
```

A system-tray icon appears. Press **Caps Lock**, speak, press again — text is pasted wherever the cursor is.

---

## Install (macOS)

```bash
cd sCREAM
make setup      # venv + python deps + whisper.cpp + model
make whisper    # terminal 1
make run        # terminal 2
```

See the [upstream README](https://github.com/adjacentai/cream-typer#readme) for full macOS docs.

---

## Windows permissions

| Permission | Why |
|---|---|
| No special permissions required | pynput and pystray work without elevation on standard user accounts |

> **Note:** Some corporate security software may block global keyboard hooks. If the hotkey doesn't fire, check your endpoint protection settings.

---

## Development

```bash
# Lint
ruff check .
ruff format --check .

# Format
ruff format .
ruff check --fix .

# Test
pytest
```

---

## Project layout

```
sCREAM/
├── src/                   # imported as `cream_typer`
│   ├── app.py             # business logic, NO platform-specific code
│   ├── config.py          # constants and transcription modes
│   ├── recorder.py        # sounddevice → WAV in memory
│   ├── transcriber.py     # HTTP client for whisper.cpp server
│   └── backend/
│       ├── __init__.py    # dispatch by sys.platform
│       ├── _base.py       # Protocol contracts
│       ├── _macos.py      # Quartz + rumps
│       └── _windows.py    # pynput + pystray + pyperclip
├── tests/
├── scripts/
│   ├── whisper_server.sh  # macOS/Linux
│   └── whisper_server.ps1 # Windows
├── pyproject.toml
├── Makefile
└── ...
```

---

## Configuration

Everything lives in `src/config.py` — hotkey, sample rate, language modes, whisper URL, etc. See the [upstream docs](https://github.com/adjacentai/cream-typer#configuration) for details.
