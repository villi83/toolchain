# Toolchain — сборка окружения (песочница Kimi)

## Состав
- armgcc_chunks/ + reassemble.sh — ARM GCC (сборка прошивок TITAN/emelya)
- kicad_chunks/ kicad_aa..ae — KiCad 10.0.6 AppImage, разбитый на чанки по ~100MB
- kicad_headless_toolkit.py — s-expr правки .kicad_sch/.kicad_pcb
- probe/, bootstrap.sh — восстановление окружения

## KiCad из чанков (ОБЯЗАТЕЛЬНО для каждого нового чата)
cat kicad_chunks/kicad_a* > /tmp/KiCad.AppImage && chmod +x /tmp/KiCad.AppImage
cd /tmp && ./KiCad.AppImage --appimage-extract   # FUSE нет, только распаковка
/tmp/squashfs-root/AppRun sch erc <проект>/titan-core.kicad_sch   # валидация ДО пуша

Скачивание чанков: https://raw.githubusercontent.com/villi83/toolchain/main/kicad_chunks/kicad_aX
(каждый чанк < 100MB, fuse-лимит /mnt/agents не касается при скачивании в /tmp)

## Правило проекта (TITAN)
Любые правки схем/плат — только после локального прогона ERC/DRC через kicad-cli.
Баланс скобок НЕ гарантирует валидность файла (уроки v2.2.37/v2.2.41).
