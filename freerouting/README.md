# Freerouting — headless автотрассировка (pipeline TITAN)

## Активы
- `fr210.jar` — Freerouting 2.1.0 (GPL-3.0, github.com/freerouting/freerouting). Требует Java 21 (НЕ 17, НЕ 25-only: v2.4.1 требует Java 25, поэтому зафиксирован 2.1.0).
- `jre21.tar.gz` — Temurin OpenJDK 21.0.12.1 JRE linux-x64 (для песочницы/WSL). На Windows ставь любой JRE/JDK 21+ или бери freerouting-*.msi с гитхаба релизов.

## Конвейер (песочница / WSL)
```bash
# 1. DSN из платы (pcbnew из AppImage KiCad):
squashfs-root/usr/bin/python3.11 tools/export_dsn.py   # ExportSpecctraDSN -> titan-main-autoroute.dsn (БЕЗ зон!)

# 2. Автотрассировка:
tar -xzf freerouting/jre21.tar.gz -C /tmp
/tmp/jdk-21.0.12.1+1-jre/bin/java -Djava.awt.headless=true -Xmx2500m \
  -jar freerouting/fr210.jar -de titan-main-autoroute.dsn -do titan-main.ses -mp 25

# 3. Импорт SES обратно в плату:
squashfs-root/usr/bin/python3.11 tools/import_ses.py   # ImportSpecctraSES -> перезаливка DGND -> DRC
```
ВАЖНО: песочница 4GB RAM — freerouting 2.1 раздувается до 6-26GB, полный прогон не тянет. Рабочий сценарий песочницы: малые платы/доукладка. Полная TITAN-MAIN — на машине пользователя (Windows, 8GB+).

## Windows (пользователь)
1. Установить JRE 21+ (adoptium Temurin) или взять freerouting-2.1.0-windows-x64.msi.
2. `java -jar fr210.jar -de titan-main-autoroute.dsn -do titan-main.ses -mp 50` — или GUI для контроля.
3. SES -> в репо (пуш) или в чат -> агент импортирует.

## Зеркала (если github медленный)
- ghfast.top / gh-proxy.com префиксом к URL релиза — проверено 12.09.26, ~1 МБ/с.
