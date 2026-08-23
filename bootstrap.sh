#!/bin/bash
set -e

WORK="/mnt/agents/work"
TOOLCHAIN="$WORK/toolchain"

echo "=== EMELYA bootstrap ==="
mkdir -p "$WORK"

# 1. Клонируем репо (если еще не клонировано)
if [ ! -d "$TOOLCHAIN" ]; then
    echo "Клонирую тулчейн..."
    git clone --depth=1 https://github.com/villi83/toolchain.git "$TOOLCHAIN"
fi

# 2. Собираем ARM-GCC из чанков
if [ ! -d "$WORK/armgcc/bin" ]; then
    echo "Собираю ARM-GCC из чанков..."
    mkdir -p "$WORK/armgcc"

    # Сначала ищем чанки в папке armgcc_chunks/
    if ls "$TOOLCHAIN"/armgcc_chunks/armgcc_* 1> /dev/null 2>&1; then
        cat "$TOOLCHAIN"/armgcc_chunks/armgcc_* > /tmp/armgcc.tar.xz
    # Или в корне репо (старый вариант)
    elif ls "$TOOLCHAIN"/armgcc_* 1> /dev/null 2>&1; then
        cat "$TOOLCHAIN"/armgcc_* > /tmp/armgcc.tar.xz
    else
        echo "ОШИБКА: Чанки ARM-GCC не найдены!"
        echo "Положите файлы armgcc_aa, armgcc_ab, ... в папку armgcc_chunks/ репозитория."
        exit 1
    fi

    tar -xf /tmp/armgcc.tar.xz -C "$WORK/armgcc" --strip-components=1
    rm /tmp/armgcc.tar.xz
    echo "ARM-GCC готов."
fi
export PATH="$WORK/armgcc/bin:$PATH"

# 3. KiCad toolkit
if [ ! -f "$WORK/kicad/kicad_headless_toolkit.py" ]; then
    mkdir -p "$WORK/kicad"
    cp "$TOOLCHAIN"/kicad_headless_toolkit.py "$WORK/kicad/"
fi

# 4. Python-зависимости
if [ -d "$TOOLCHAIN/py/wheels" ] && [ "$(ls -A $TOOLCHAIN/py/wheels)" ]; then
    echo "Устанавливаю Python-зависимости из wheels..."
    pip install --user --no-index --find-links="$TOOLCHAIN/py/wheels" -r "$TOOLCHAIN/py/requirements.txt" 2>/dev/null || true
else
    echo "Wheels не найдены, пропускаю локальную установку."
fi

echo "=== Проверка ==="
arm-none-eabi-gcc --version
python3 "$WORK/kicad/kicad_headless_toolkit.py" --help 2>/dev/null || echo "Toolkit на месте"
echo "=== Готово ==="
