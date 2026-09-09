Положите сюда чанки KiCad AppImage:
- kicad_aa
- kicad_ab
- kicad_ac
(и т.д., пока файл не закончится)

Как сделать чанки:
1. Возьмите файл KiCad-*.AppImage (Linux x86_64, та версия, на которой
   собраны платы в source/templates).
2. Разбейте на части по 95 МБ:
   Linux/Mac: split -b 95m KiCad-*.AppImage kicad_
   Windows: 7-Zip → Разбить архив → 95M
3. Переименуйте части в kicad_aa, kicad_ab, kicad_ac, ...
4. Загрузите их в эту папку (файлы .001/.002/.7z из конца переименуйте
   в этот формент — bootstrap собирает строго по маске kicad_*).

Сборка (делает bootstrap.sh автоматически):
   cat kicad_* > KiCad.AppImage
   chmod +x KiCad.AppImage
   ./KiCad.AppImage --appimage-extract   # -> squashfs-root/
