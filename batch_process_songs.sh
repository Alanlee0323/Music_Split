#!/usr/bin/env bash

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/split_drums.py"
SOURCE_DIR="$SCRIPT_DIR/original_songs"
MODEL="htdemucs_ft"
CONDA_ENV="${CONDA_ENV:-newyolov5}"
CONDA_HOME_UNIX="${CONDA_HOME_UNIX:-$HOME/anaconda3}"
CONDA_PYTHON_UNIX="${CONDA_PYTHON_UNIX:-$CONDA_HOME_UNIX/envs/$CONDA_ENV/python.exe}"
CONDA_PYTHON_UNIX_ALT="$CONDA_HOME_UNIX/envs/$CONDA_ENV/bin/python"
if command -v cygpath >/dev/null 2>&1; then
  CONDA_PYTHON_WIN="${CONDA_PYTHON_WIN:-$(cygpath -w "$CONDA_PYTHON_UNIX" 2>/dev/null || true)}"
else
  CONDA_PYTHON_WIN="${CONDA_PYTHON_WIN:-}"
fi

SUPPORTED_EXTENSIONS=("mp3" "wav" "flac" "ogg" "m4a" "aac" "wma" "aiff")

clear
echo
echo "========================================================"
echo "Drum Splitter"
echo "========================================================"
echo

if [[ ! -f "$PYTHON_SCRIPT" ]]; then
  echo "Python script not found: $PYTHON_SCRIPT"
  exit 1
fi

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Source directory not found: $SOURCE_DIR"
  exit 1
fi

if [[ -x "$CONDA_PYTHON_UNIX" ]]; then
  PYTHON_EXE="$CONDA_PYTHON_UNIX"
elif [[ -x "$CONDA_PYTHON_UNIX_ALT" ]]; then
  PYTHON_EXE="$CONDA_PYTHON_UNIX_ALT"
elif [[ -n "$CONDA_PYTHON_WIN" && -f "$CONDA_PYTHON_WIN" ]]; then
  PYTHON_EXE="$CONDA_PYTHON_WIN"
elif command -v python >/dev/null 2>&1; then
  PYTHON_EXE="python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_EXE="python3"
else
  echo "No usable Python executable was found."
  exit 1
fi

MODE_LABEL=""
KEEP_DRUMS=0

select_mode() {
  while true; do
    echo "Select output mode"
    echo "[1] Keep drums only (drums.wav)"
    echo "[2] Remove drums (no_drums.wav)"
    echo "[q] Cancel"
    read -r -n 1 -p "Press 1, 2, or q: " choice
    echo
    case "$choice" in
      1)
        KEEP_DRUMS=1
        MODE_LABEL="Keep drums only (drums.wav)"
        return 0
        ;;
      2)
        KEEP_DRUMS=0
        MODE_LABEL="Remove drums (no_drums.wav)"
        return 0
        ;;
      q|Q)
        return 1
        ;;
    esac
    echo "Please enter 1, 2, or q."
    echo
  done
}

collect_songs() {
  SONGS=()
  local path lower ext
  shopt -s nullglob
  for path in "$SOURCE_DIR"/*; do
    [[ -f "$path" ]] || continue
    lower="${path##*.}"
    lower="${lower,,}"
    for ext in "${SUPPORTED_EXTENSIONS[@]}"; do
      if [[ "$lower" == "$ext" ]]; then
        SONGS+=("$path")
        break
      fi
    done
  done
  shopt -u nullglob

  if [[ ${#SONGS[@]} -eq 0 ]]; then
    echo "No supported audio files were found in $SOURCE_DIR"
    return 1
  fi

  IFS=$'\n' SONGS=($(printf '%s\n' "${SONGS[@]}" | sort))
  unset IFS
  return 0
}

draw_menu() {
  local current_index="$1"
  local start_index="$2"
  local visible_count="$3"
  local total="${#SONGS[@]}"
  local end_index=$((start_index + visible_count - 1))
  local i name

  (( end_index >= total )) && end_index=$((total - 1))

  clear
  echo
  echo "========================================================"
  echo "Select a song to process"
  echo "========================================================"
  echo
  echo "Use Up/Down to move, Enter to confirm, q to cancel"
  echo

  for ((i = start_index; i <= end_index; i++)); do
    name="$(basename "${SONGS[i]}")"
    if [[ "$i" -eq "$current_index" ]]; then
      printf '> %s\n' "$name"
    else
      printf '  %s\n' "$name"
    fi
  done

  echo
  echo "Song $((current_index + 1)) / $total"
}

select_song() {
  collect_songs || return 1

  local selected_index=0
  local top_index=0
  local visible_count=10
  local key

  if [[ -n "${LINES:-}" && "$LINES" -gt 8 ]]; then
    visible_count=$((LINES - 8))
  fi

  if (( visible_count < 5 )); then
    visible_count=5
  fi

  if (( visible_count > ${#SONGS[@]} )); then
    visible_count=${#SONGS[@]}
  fi

  while true; do
    if (( selected_index < top_index )); then
      top_index=$selected_index
    fi

    if (( selected_index >= top_index + visible_count )); then
      top_index=$((selected_index - visible_count + 1))
    fi

    draw_menu "$selected_index" "$top_index" "$visible_count"

    IFS= read -rsn1 key
    if [[ "$key" == $'\x1b' ]]; then
      IFS= read -rsn1 -t 0.1 key || true
      if [[ "$key" == "[" ]]; then
        IFS= read -rsn1 -t 0.1 key || true
        case "$key" in
          A)
            if (( selected_index > 0 )); then
              ((selected_index--))
            else
              selected_index=$((${#SONGS[@]} - 1))
            fi
            ;;
          B)
            if (( selected_index < ${#SONGS[@]} - 1 )); then
              ((selected_index++))
            else
              selected_index=0
            fi
            ;;
        esac
      else
        return 1
      fi
    elif [[ -z "$key" ]]; then
      SELECTED_FILE="${SONGS[selected_index]}"
      return 0
    elif [[ "$key" == "q" || "$key" == "Q" ]]; then
      return 1
    fi
  done
}

if ! select_mode; then
  echo
  echo "Operation cancelled."
  exit 0
fi

if ! select_song; then
  echo
  echo "Operation cancelled."
  exit 0
fi

SELECTED_NAME="$(basename "$SELECTED_FILE")"

echo
echo "========================================================"
echo "Ready to process"
echo "========================================================"
echo "Song: $SELECTED_NAME"
echo "Mode: $MODE_LABEL"
echo "Model: $MODEL"
echo

CMD=("$PYTHON_EXE" "$PYTHON_SCRIPT" "$SELECTED_FILE" "--model" "$MODEL")
if [[ "$KEEP_DRUMS" -eq 1 ]]; then
  CMD+=("--keep-drums")
fi

"${CMD[@]}"
status=$?

echo
if [[ "$status" -ne 0 ]]; then
  echo "Processing failed: $SELECTED_NAME"
else
  echo "Processing complete: $SELECTED_NAME"
fi

echo
echo "========================================================"
echo "Done"
echo "========================================================"

exit "$status"
