#!/bin/bash

# Tanlangan loyiha katalogi
PROJECT_PATH=$1

# Venv katalogi
VENV_PATH="$PROJECT_PATH/venv/bin/activate"

# Tekshirish: venv mavjudmi?
if [ -f "$VENV_PATH" ]; then
    echo "Venv topildi. Faollashtirilmoqda..."
    source "$VENV_PATH"
    echo "Virtual muhit faollashtirildi: $PROJECT_PATH"
else
    echo "Xatolik: $VENV_PATH mavjud emas. Iltimos, to'g'ri katalogni tanlang."
fi
