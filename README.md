# toolchain — окружение EMELYA/TITAN

Восстановление рабочего окружения в ЛЮБОМ новом чате (2 команды):

```bash
export GITHUB_TOKEN=ghp_xxxxxxxx   # токен доступа к GitHub
bash <(curl -s https://raw.githubusercontent.com/villi83/toolchain/main/bootstrap.sh)
```

## Что bootstrap делает
1. Клонирует `villi83/toolchain` (public) → `/tmp/emelya_env/toolchain`
2. Клонирует `villi83/source` (private, нужен токен) → `/tmp/emelya_env/source`
3. Собирает ARM-GCC из `armgcc_chunks/armgcc_*` → `/tmp/emelya_env/armgcc`
4. Собирает KiCad AppImage из `kicad_chunks/kicad_*` → `/tmp/emelya_env/squashfs-root`
5. Ставит python-wheels из `py/wheels` (без сети)
6. Показывает начало `PROJECT_STATE.md` — его читать ПЕРВЫМ в работе над проектом

## Железные правила
- **/tmp эфемерен.** Между чатами всё исчезает. Правки пушить в
  `villi83/source` в ТОМ ЖЕ чате, где делались. Данные, которые жалко терять,
  держать только в репозитории.
- **/mnt/agents — fuse-портал облака, лимит 100 МБ на файл.** Git-клоны туда
  падают с I/O error. Большие файлы только чанками <95 МБ.
- **Платы — через KiCad AppImage** (pcbnew/kicad-cli из squashfs-root).
  Все платы в `source/templates` сделаны так. Текстовый
  `kicad_headless_toolkit.py` — запасной путь, не основной.

## Чанки
| Папка | Источник | Сборка |
|---|---|---|
| `armgcc_chunks/` | arm-gnu-toolchain-13.3.rel1-x86_64-arm-none-eabi.tar.xz | `cat armgcc_* > t.tar.xz && tar xf` |
| `kicad_chunks/` | KiCad-*.AppImage | `cat kicad_* > KiCad.AppImage && ./KiCad.AppImage --appimage-extract` |

Как резать: `split -b 95m ФАЙЛ Префикс_` → получатся `Префикс_aa`, `ab`, ...
Порядок частей важен (лексикографический: aa, ab, ac, ... az, ba, ...).
