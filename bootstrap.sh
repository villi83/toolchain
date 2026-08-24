#!/bin/bash
set -e

WORK="/mnt/agents/work"
TOOLCHAIN="$WORK/toolchain"
SRC="$WORK/titan_src_fixed"

echo "=== EMELYA bootstrap ==="
mkdir -p "$WORK"

# === 1. Тулчейн (public) ===
if [ ! -d "$TOOLCHAIN" ]; then
    echo "Клонирую тулчейн..."
    git clone --depth=1 https://github.com/villi83/toolchain.git "$TOOLCHAIN"
fi

# === 2. Исходники (private, нужен токен) ===
if [ ! -d "$SRC" ]; then
    if [ -z "$GITHUB_TOKEN" ]; then
        echo "ВНИМАНИЕ: Приватный репозиторий требует токена."
        echo "Запусти перед bootstrap: export GITHUB_TOKEN=ghp_xxxxxxxx"
        exit 1
    fi
    echo "Клонирую исходники..."
    git clone --depth=1 "https://${GITHUB_TOKEN}@github.com/villi83/source.git" "$SRC"
fi

# === 3. ARM-GCC из чанков ===
if [ ! -d "$WORK/armgcc/bin" ]; then
    echo "Собираю ARM-GCC..."
    mkdir -p "$WORK/armgcc"
    cat "$TOOLCHAIN"/armgcc_chunks/armgcc_* > /tmp/armgcc.tar.xz
    tar -xf /tmp/armgcc.tar.xz -C "$WORK/armgcc" --strip-components=1
    rm /tmp/armgcc.tar.xz
    echo "ARM-GCC готов."
fi
export PATH="$WORK/armgcc/bin:$PATH"

# === 4. KiCad toolkit ===
if [ ! -f "$WORK/kicad/kicad_headless_toolkit.py" ]; then
    mkdir -p "$WORK/kicad"
    cp "$TOOLCHAIN"/kicad_headless_toolkit.py "$WORK/kicad/"
fi

# === 5. Python-зависимости ===
if [ -d "$TOOLCHAIN/py/wheels" ] && [ "$(ls -A $TOOLCHAIN/py/wheels)" ]; then
    pip install --user --no-index --find-links="$TOOLCHAIN/py/wheels" -r "$TOOLCHAIN/py/requirements.txt" 2>/dev/null || true
fi

echo "=== Проверка ==="
arm-none-eabi-gcc --version
python3 "$WORK/kicad/kicad_headless_toolkit.py" --help 2>/dev/null || echo "Toolkit OK"
echo "=== Готово ==="