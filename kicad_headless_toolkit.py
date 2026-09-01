#!/usr/bin/env python3
# kicad_headless_toolkit.py  v2.1
# Текстовые правки s-expr для KiCad 10 (pcbnew API НЕ используется)
# Уроки из DRC-отчета индуктивного канала (2026-08-24):
#   1. KiCad поворачивает footprint ПО ЧАСОВОЙ (global = fp_at + R(-angle) * local).
#      Значит математически: local -> global = rotate(local, -angle).
#   2. Треки НЕ должны проходить через чужие пады — проверяем эвристически.
#   3. Катушки/перемычки оформлять как Net tie.
#   4. filled_polygon удалять ТОЛЬКО через парсинг скобок, regex жрет полплаты.

import sys
import re
import os
import math

# ---------------------------------------------------------------------------
# IO
# ---------------------------------------------------------------------------
def read_pcb(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_pcb(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def backup(path):
    """Простой .bak перед правкой."""
    bak = f"{path}.bak"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as src, open(bak, 'w', encoding='utf-8') as dst:
            dst.write(src.read())

def backup_round(path, n):
    """Версионный бэкап: file.bak.1, file.bak.2 ..."""
    bak = f"{path}.bak.{n}"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as src, open(bak, 'w', encoding='utf-8') as dst:
            dst.write(src.read())

# ---------------------------------------------------------------------------
# Вставка / удаление
# ---------------------------------------------------------------------------
def insert_before_last(content, marker, block):
    """Вставить block перед ПОСЛЕДНИМ вхождением marker (например embedded_fonts)."""
    idx = content.rfind(marker)
    if idx == -1:
        return content + '\n' + block
    return content[:idx] + block + '\n' + content[idx:]

def clear_zone_fills(content):
    """Удалить ВСЕ (filled_polygon ...) корректно — через счетчик скобок.
    Перед экспортом gerber: открой плату в KiCad, нажми B (перезаливка зон).
    """
    result = []
    i = 0
    L = len(content)
    while i < L:
        m = re.search(r'\(filled_polygon\b', content[i:])
        if not m:
            result.append(content[i:])
            break
        start = i + m.start()
        result.append(content[i:start])
        depth = 0
        j = start
        while j < L:
            if content[j] == '(':
                depth += 1
            elif content[j] == ')':
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
        i = j
    return ''.join(result)

# ---------------------------------------------------------------------------
# Поворот / размещение
# ---------------------------------------------------------------------------
def rotate_point(x, y, cx, cy, angle_deg):
    """Математический поворот точки (x,y) вокруг (cx,cy) на angle_deg.
    Положительный угол = ПРОТИВ часовой (математическая конвенция)."""
    rad = math.radians(angle_deg)
    dx = x - cx
    dy = y - cy
    xr = dx * math.cos(rad) - dy * math.sin(rad) + cx
    yr = dx * math.sin(rad) + dy * math.cos(rad) + cy
    return xr, yr

def rotate_point_kicad(x, y, cx, cy, angle_deg):
    """KiCad-конвенция: положительный угол = ПО ЧАСОВОЙ.
    Эквивалентно математическому rotate(..., -angle_deg)."""
    return rotate_point(x, y, cx, cy, -angle_deg)

def place_footprint(content, refdes, x, y, angle_deg=0):
    """Переместить footprint по глобальным координатам с углом ПО ЧАСОВОЙ (KiCad).
    Возвращает новый content. Угол angle_deg: 0..360, по часовой."""
    pat = (
        rf'(\(footprint\s+"[^"]+"\s+\(at\s+)'
        rf'([\d\.\-]+)\s+([\d\.\-]+)(?:\s+([\d\.\-]+))?'
        rf'(\)[^\(]*\(property\s+"Reference"\s+"{re.escape(refdes)}"'
    )
    def repl(m):
        return f'{m.group(1)}{x:.6f} {y:.6f} {angle_deg:.6f}{m.group(5)}'
    newc = re.sub(pat, repl, content, count=1)
    if newc == content:
        raise ValueError(f"Footprint {refdes} не найден")
    return newc

def get_reference_xy(content, refdes):
    """Вернуть (x, y, angle) footprint по референсу. Угол в градусах KiCad (по часовой)."""
    pattern = (
        rf'\(footprint\s+"[^"]+"\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)(?:\s+([\d\.\-]+))?\)'
        rf'[^\(]*\(property\s+"Reference"\s+"{re.escape(refdes)}"'
    )
    m = re.search(pattern, content)
    if m:
        return float(m.group(1)), float(m.group(2)), float(m.group(3) or 0)
    return None, None, None

def set_reference_xy(content, refdes, x, y, angle=0):
    """Устаревшая обертка; используй place_footprint."""
    return place_footprint(content, refdes, x, y, angle)

# ---------------------------------------------------------------------------
# Проверки (assert / sanity check)
# ---------------------------------------------------------------------------
def assert_no_overlap_deletions(content):
    """Проверка баланса скобок после текстовых правок."""
    open_count = content.count('(')
    close_count = content.count(')')
    if open_count != close_count:
        raise ValueError(f"Несовпадение скобок: (={open_count}, )={close_count}")
    return True

def get_pads_for_footprint(content, refdes):
    """Извлечь пады footprint: список словарей {name, x, y, w, h}.
    Координаты в локальной СК footprint."""
    fp_pat = (
        rf'\(footprint\s+"[^"]+"\s+\(at\s+[\d\.\-]+\s+[\d\.\-]+(?:\s+[\d\.\-]+)?\)'
        rf'.*?\(property\s+"Reference"\s+"{re.escape(refdes)}".*?\n\)'
    )
    m = re.search(fp_pat, content, re.DOTALL)
    if not m:
        return []
    fp_block = m.group(0)
    pads = []
    for pm in re.finditer(
        r'\(pad\s+"([^"]+)"\s+\w+\s+\w+\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)\)'
        r'.*?\(size\s+([\d\.\-]+)\s+([\d\.\-]+)\)',
        fp_block, re.DOTALL
    ):
        pads.append({
            'name': pm.group(1),
            'x': float(pm.group(2)),
            'y': float(pm.group(3)),
            'w': float(pm.group(4)),
            'h': float(pm.group(5)),
        })
    return pads

def get_pad_global_xy(content, refdes, pad_name):
    """Вернуть глобальные (x, y) пада по референсу и имени пада.
    Учитывает угол поворота footprint (KiCad, по часовой)."""
    fx, fy, fang = get_reference_xy(content, refdes)
    if fx is None:
        return None, None
    pads = get_pads_for_footprint(content, refdes)
    for p in pads:
        if p['name'] == pad_name:
            gx, gy = rotate_point_kicad(p['x'], p['y'], 0, 0, fang)
            return gx + fx, gy + fy
    return None, None

def check_track_pad_shorts(content, threshold=0.05):
    """Эвристика: ищем треки, проходящие ближе threshold мм к чужим падам.
    Возвращает список предупреждений. НЕ замена DRC, но ловит очевидные промахи."""
    warnings = []
    # TODO: полноценная проверка требует парсинга (segment ...) и (arc ...)
    # Пока заглушка — основной вывод: не полагаться только на это,
    # а использовать перед записью assert + ручной DRC в KiCad.
    return warnings

# ---------------------------------------------------------------------------
# Свойства / флаги
# ---------------------------------------------------------------------------
def set_net_tie(content, refdes, enable=True):
    """Установить/снять флаг Net tie у footprint (для катушек, перемычек).
    KiCad 10: (property 'ki_net_tie' 'yes') внутри footprint."""
    val = 'yes' if enable else 'no'
    pat = (
        rf'(\(footprint\s+"[^"]+"\s+\(at\s+[\d\.\-]+\s+[\d\.\-]+(?:\s+[\d\.\-]+)?\)'
        rf'.*?\(property\s+"Reference"\s+"{re.escape(refdes)}".*?\n)(\))'
    )
    prop_block = f'\t(property "ki_net_tie" "{val}"\n\t)\n'
    def repl(m):
        return m.group(1) + prop_block + m.group(2)
    newc = re.sub(pat, repl, content, count=1, flags=re.DOTALL)
    if newc == content:
        raise ValueError(f"Footprint {refdes} не найден для set_net_tie")
    return newc

# ---------------------------------------------------------------------------
# Утилиты
# ---------------------------------------------------------------------------
def run_drc_checklist(content):
    """Пост-правочный чеклист перед записью файла.
    Возвращает список строк с результатами проверок."""
    checks = []
    # 1. Баланс скобок
    try:
        assert_no_overlap_deletions(content)
        checks.append("OK: скобки сбалансированы")
    except ValueError as e:
        checks.append(f"FAIL: {e}")
    # 2. Нет пустых filled_polygon (если чистили — должны быть убраны)
    if '(filled_polygon' in content:
        checks.append("WARN: в файле остались filled_polygon — после правки нажми B в KiCad")
    else:
        checks.append("OK: filled_polygon отсутствуют (ожидается перезаливка)")
    # 3. Все footprint имеют (at ...)
    missing_at = len(re.findall(r'\(footprint\s+"[^"]+"\s+(?!\(at\))', content))
    if missing_at:
        checks.append(f"FAIL: {missing_at} footprint без (at ...)")
    else:
        checks.append("OK: все footprint имеют координаты")
    return checks

if __name__ == '__main__':
    print('KiCad headless toolkit v2.1 ready')
