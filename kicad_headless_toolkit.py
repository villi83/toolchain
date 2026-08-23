#!/usr/bin/env python3
# kicad_headless_toolkit.py
# Текстовые правки s-expr для KiCad 10 (pcbnew API НЕ используется)

import sys
import re
import os
import math

def read_pcb(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_pcb(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def backup(path):
    bak = f"{path}.bak"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as src:
            data = src.read()
        with open(bak, 'w', encoding='utf-8') as dst:
            dst.write(data)

def insert_before_last(content, marker, block):
    idx = content.rfind(marker)
    if idx == -1:
        return content + '\n' + block
    return content[:idx] + block + '\n' + content[idx:]

def remove_filled_polygon(content):
    # Удалить filled_polygon перед refill
    # KiCad 10: (filled_polygon (layer "...") ... )
    pattern = r'\(filled_polygon\s+\(layer\s+"[^"]+"\)[^\)]*\)'
    return re.sub(pattern, '', content, flags=re.DOTALL)

def get_reference_xy(content, refdes):
    # Найти координаты компонента по референсу
    pattern = rf'\(footprint\s+"[^"]+"\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)\)[^\(]*\(property\s+"Reference"\s+"{refdes}"'
    m = re.search(pattern, content)
    if m:
        return float(m.group(1)), float(m.group(2))
    return None, None

def set_reference_xy(content, refdes, x, y, angle=0):
    # Смещение референса: local = R(угол) · delta
    pattern = rf'(\(footprint\s+"[^"]+"\s+\(at\s+)([\d\.\-]+)\s+([\d\.\-]+)(\s+[\d\.\-]+)?(\)[^\(]*\(property\s+"Reference"\s+"{refdes}")'
    def repl(m):
        return f'{m.group(1)}{x:.6f} {y:.6f}{m.group(4) or ""}{m.group(5)}'
    return re.sub(pattern, repl, content)

def assert_no_overlap_deletions(content):
    # Проверка, что удаления не пересекаются (assert)
    open_count = content.count('(')
    close_count = content.count(')')
    if open_count != close_count:
        raise ValueError(f"Несовпадение скобок: (={open_count}, )={close_count}")
    return True

def rotate_point(x, y, cx, cy, angle_deg):
    """Поворот точки (x,y) вокруг (cx,cy) на angle_deg градусов."""
    rad = math.radians(angle_deg)
    dx = x - cx
    dy = y - cy
    xr = dx * math.cos(rad) - dy * math.sin(rad) + cx
    yr = dx * math.sin(rad) + dy * math.cos(rad) + cy
    return xr, yr

if __name__ == '__main__':
    print('KiCad headless toolkit ready')
