#!/bin/bash

# === Einstellungen ===
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"
MAIN_SCRIPT="main.py"

# === 1. Virtuelle Umgebung prüfen / erstellen ===
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists."
fi

# === 2. Virtuelle Umgebung aktivieren ===
# Shell-kompatibel aktivieren
if [ -f "$VENV_DIR/Scripts/activate" ]; then
    # Windows
    source "$VENV_DIR/Scripts/activate"
else
    # Linux/macOS
    source "$VENV_DIR/bin/activate"
fi



# === 3. Anforderungen installieren ===
python -m pip install --upgrade pip
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
    python "$MAIN_SCRIPT" >> log.txt 2>&1
else
    echo "Error: $MAIN_SCRIPT wasn't found!"
    exit 1
fi
