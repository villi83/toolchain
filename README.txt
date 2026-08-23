Репозиторий: https://github.com/villi83/toolchain

Состав:
-------
- armgcc_chunks/       — чанки ARM-GCC (вы добавляете сами)
- kicad_headless_toolkit.py — текстовые правки s-expr KiCad 10
- bootstrap.sh         — сборка окружения в песочнице Kimi
- py/requirements.txt  — Python-зависимости
- py/wheels/           — папка для .whl файлов (пока пустая)

Важно:
------
- KiCad AppImage НЕ храним здесь — работаем только s-expr.
- Папка py/wheels может быть пустой — Kimi скачает библиотеки сам.
- bootstrap.sh уже настроен на username villi83.
