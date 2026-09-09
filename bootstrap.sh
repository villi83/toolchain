#!/bin/bash
# ============================================================
# EMELYA bootstrap v2 — восстановление окружения в новом чате
# ============================================================
# ВАЖНО (прочитать перед запуском):
#  1. Всё собирается в /tmp — ЭФЕМЕРНО, между чатами исчезает.
#     Все правки пушить обратно в github.com/villi83/source
#     В ТОМ ЖЕ ЧАТЕ, где делались.
#  2. /mnt/agents (fuse-портал облака) НЕ подходит для git-клонов:
#     запись pack-файла падает с I/O error, лимит 100 МБ на файл.
#  3. Перед запуском: export GITHUB_TOKEN=ghp_xxxxxxxx
#     (нужен для приватного репо villi83/source)
# ============================================================
set -e

ENV="/tmp/emelya_env"          # корень окружения (эфемерный!)
TOOLCHAIN="$ENV/toolchain"     # public: чанки тулчейна/кикада, toolkit, wheels
SRC="$ENV/source"              # private: исходники, платы, PROJECT_STATE.md

echo "=== EMELYA bootstrap v2 ==="
mkdir -p "$ENV"

# === 1. toolchain (public) ===
if [ ! -d "$TOOLCHAIN/.git" ]; then
    echo "Клонирую toolchain..."
    git clone --depth=1 https://github.com/villi83/toolchain.git "$TOOLCHAIN"
fi

# === 2. source (private, нужен токен) ===
if [ ! -d "$SRC/.git" ]; then
    if [ -z "$GITHUB_TOKEN" ]; then
        echo "ОШИБКА: export GITHUB_TOKEN=ghp_xxxxxxxx и запусти снова."
        exit 1
    fi
    echo "Клонирую source..."
    git clone --depth=1 "https://${GITHUB_TOKEN}@github.com/villi83/source.git" "$SRC"
fi

# === 3. ARM-GCC из чанков (armgcc_aa + armgcc_ab + ... -> tar.xz) ===
if [ ! -x "$ENV/armgcc/bin/arm-none-eabi-gcc" ]; then
    echo "Собираю ARM-GCC из чанков..."
    cat "$TOOLCHAIN"/armgcc_chunks/armgcc_* > "$ENV/armgcc.tar.xz"
    mkdir -p "$ENV/armgcc"
    tar -xf "$ENV/armgcc.tar.xz" -C "$ENV/armgcc" --strip-components=1
    rm "$ENV/armgcc.tar.xz"
    echo "ARM-GCC готов."
fi
export PATH="$ENV/armgcc/bin:$PATH"

# === 4. KiCad AppImage из чанков (kicad_aa + kicad_ab + ...) ===
# Сборка плат — ТОЛЬКО через AppImage (pcbnew CLI).
# Текстовый kicad_headless_toolkit.py — запасной вариант, платы
# из source/templates собраны через AppImage, не через текстовые правки.
if [ ! -x "$ENV/squashfs-root/usr/bin/kicad" ]; then
    if ls "$TOOLCHAIN"/kicad_chunks/kicad_* >/dev/null 2>&1; then
        echo "Собираю KiCad AppImage из чанков..."
        cat "$TOOLCHAIN"/kicad_chunks/kicad_* > "$ENV/KiCad.AppImage"
        chmod +x "$ENV/KiCad.AppImage"
        cd "$ENV" && ./KiCad.AppImage --appimage-extract   # -> squashfs-root/
        rm "$ENV/KiCad.AppImage"
        echo "KiCad готов (squashfs-root)."
    else
        echo "ВНИМАНИЕ: kicad_chunks/ пуст — KiCad НЕ собран."
        echo "Платы не трогать до загрузки чанков в репо!"
    fi
fi
export PATH="$ENV/squashfs-root/usr/bin:$PATH"

# === 5. Python-зависимости (wheels из репо, без сети) ===
if [ -d "$TOOLCHAIN/py/wheels" ] && [ "$(ls -A "$TOOLCHAIN/py/wheels")" ]; then
    pip install --user --no-index --find-links="$TOOLCHAIN/py/wheels" \
        -r "$TOOLCHAIN/py/requirements.txt" 2>/dev/null || true
fi

# === 6. Состояние проекта (читать первым!) ===
if [ -f "$SRC/PROJECT_STATE.md" ]; then
    echo "--- PROJECT_STATE.md (первые 40 строк) ---"
    head -40 "$SRC/PROJECT_STATE.md"
fi

# === 7. Проверка ===
echo "=== Проверка ==="
arm-none-eabi-gcc --version | head -1
kicad-cli version 2>/dev/null || echo "KiCad CLI недоступен (нет чанков?)"
echo "ENV=$SRC (source) | $TOOLCHAIN (toolchain)"
echo "=== Готово ==="
