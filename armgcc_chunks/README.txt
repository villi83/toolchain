Положите сюда чанки ARM-GCC:
- armgcc_aa
- armgcc_ab
- armgcc_ac
- armgcc_ad
(и т.д., если больше)

Как сделать чанки:
1. Скачайте arm-gnu-toolchain-13.3.rel1-x86_64-arm-none-eabi.tar.xz
2. Разбейте на части по 95 МБ:
   Windows: 7-Zip → Разбить архив → 95M
   Linux/Mac: split -b 95m файл.tar.xz armgcc_
3. Переименуйте полученные части в armgcc_aa, armgcc_ab и т.д.
4. Загрузите их в эту папку на GitHub.
