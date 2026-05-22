# Launch the whisper.cpp server on Windows.
# Alternative to `make whisper` when running from PowerShell directly.
# Defaults match the Makefile — after setup everything lives in vendor\whisper.cpp\.

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $PSCommandPath)

$WhisperDir    = if ($env:WHISPER_DIR)    { $env:WHISPER_DIR }    else { Join-Path $Root "vendor\whisper.cpp" }
$WhisperServer = if ($env:WHISPER_SERVER) { $env:WHISPER_SERVER } else { Join-Path $WhisperDir "build\bin\Release\whisper-server.exe" }
$WhisperModel  = if ($env:WHISPER_MODEL)  { $env:WHISPER_MODEL }  else { Join-Path $WhisperDir "models\ggml-large-v3-turbo-q5_0.bin" }
$WhisperPort   = if ($env:WHISPER_PORT)   { $env:WHISPER_PORT }   else { "8080" }
$WhisperLang   = if ($env:WHISPER_LANG)   { $env:WHISPER_LANG }   else { "en" }

& $WhisperServer --model $WhisperModel --host 127.0.0.1 --port $WhisperPort --language $WhisperLang
