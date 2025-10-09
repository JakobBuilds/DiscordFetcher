#!/bin/bash

# === Einstellungen ===
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"
MAIN_SCRIPT="main.py"

# === 1. Virtuelle Umgebung prüfen / erstellen ===
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists."
fi

# === 2. Virtuelle Umgebung aktivieren ===
# Shell-kompatibel aktivieren
source "$VENV_DIR/bin/activate"

# === 3. Anforderungen installieren ===
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing dependencies from $REQUIREMENTS_FILE..."
    pip install --upgrade pip > /dev/null
    pip install -r "$REQUIREMENTS_FILE"
else
    echo "Couldn't find $REQUIREMENTS_FILE omitting Installation."
fi

# === 4. main.py starten ===
if [ -f "$MAIN_SCRIPT" ]; then
    echo "Starting $MAIN_SCRIPT..."
    python "$MAIN_SCRIPT"
else
    echo "Error: $MAIN_SCRIPT wasn't found!"
    exit 1
fi
