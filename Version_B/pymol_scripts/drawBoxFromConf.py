#!/usr/bin/env python3
"""
drawBoxFromConf.py -- Draws a bounding box in PyMOL from a configuration file with precomputed center and size.

Usage (CLI):
    pymol -cq drawBoxFromConf.py <conf_file> [--lineWidth <width>] [--color R G B] [--dry-run]

Usage (PyMOL command):
    run drawBoxFromConf.py
    drawBoxFromConf <conf_file> [lineWidth] [R] [G] [B] [dry]

Examples:
    # From command line in any shell:
    pymol -cq drawBoxFromConf.py BACE2_6UJ0.conf --lineWidth 2.0 --color 1.0 0.0 0.0

    # Inside an interactive PyMOL session:
    PyMOL> run drawBoxFromConf.py
    PyMOL> drawBoxFromConf BACE2_6UJ0.conf 2.0 0.0 1.0 0.0
    # For dry-run:
    PyMOL> drawBoxFromConf BACE2_6UJ0.conf dry
"""
import os
import sys

# Attempt to import PyMOL API
try:
    from pymol import cmd
    from pymol.cgo import LINEWIDTH, BEGIN, LINES, COLOR, VERTEX, END
except ImportError:
    cmd = None


def _read_conf(conf_file):
    centers = {}
    sizes = {}
    with open(conf_file) as f:
        for line in f:
            if '=' in line:
                key, val = [x.strip() for x in line.split('=', 1)]
                if key.startswith('center_'):
                    centers[key] = float(val)
                elif key.startswith('size_'):
                    sizes[key] = float(val)
    return centers, sizes


def _build_box_cgo(center, size, lineWidth, color):
    cx, cy, cz = center
    sx, sy, sz = size
    minX, maxX = cx - sx/2.0, cx + sx/2.0
    minY, maxY = cy - sy/2.0, cy + sy/2.0
    minZ, maxZ = cz - sz/2.0, cz + sz/2.0

    corners = [
        (minX, minY, minZ), (minX, minY, maxZ),
        (minX, maxY, minZ), (minX, maxY, maxZ),
        (maxX, minY, minZ), (maxX, minY, maxZ),
        (maxX, maxY, minZ), (maxX, maxY, maxZ)
    ]
    edges = [
        (0,1), (2,3), (4,5), (6,7),
        (0,2), (1,3), (4,6), (5,7),
        (0,4), (1,5), (2,6), (3,7)
    ]
    box = [LINEWIDTH, lineWidth, BEGIN, LINES, COLOR, *color]
    for i, j in edges:
        box += [VERTEX, *corners[i], VERTEX, *corners[j]]
    box += [END]
    return box


def drawBoxFromConf(conf_file, lineWidth=2.0, r=1.0, g=1.0, b=1.0, dry_run=False):
    """PyMOL command: drawBoxFromConf <conf_file> [lineWidth] [r] [g] [b] [dry]"""
    conf_file = os.path.expanduser(conf_file)
    if not os.path.isfile(conf_file):
        print(f"Config file not found: {conf_file}")
        return

    centers, sizes = _read_conf(conf_file)
    required_c = ('center_x', 'center_y', 'center_z')
    required_s = ('size_x', 'size_y', 'size_z')
    if not all(k in centers for k in required_c) or not all(k in sizes for k in required_s):
        print("Config file must define center_x, center_y, center_z, size_x, size_y, size_z")
        return

    center = (centers['center_x'], centers['center_y'], centers['center_z'])
    size   = (sizes['size_x'], sizes['size_y'], sizes['size_z'])
    color  = (r, g, b)

    # Dry-run: print computed coords
    if dry_run:
        cx, cy, cz = center
        sx, sy, sz = size
        print(f"Center: ({cx:.3f}, {cy:.3f}, {cz:.3f})")
        print(f"Size:   ({sx:.3f}, {sy:.3f}, {sz:.3f})")
        print("Computed bounding box:")
        print(f"  X: {cx - sx/2:.3f} to {cx + sx/2:.3f}")
        print(f"  Y: {cy - sy/2:.3f} to {cy + sy/2:.3f}")
        print(f"  Z: {cz - sz/2:.3f} to {cz + sz/2:.3f}")
        return

    # Build and load CGO box
    if cmd is None:
        print("PyMOL API not available. Load this script within PyMOL.")
        return
    box_cgo = _build_box_cgo(center, size, lineWidth, color)
    name = 'box_' + os.path.splitext(os.path.basename(conf_file))[0]
    cmd.load_cgo(box_cgo, name)
    print(f"Running: drawBoxFromConf {conf_file} {lineWidth} {r} {g} {b}")
    print(f"Box '{name}' drawn.")

# Register as PyMOL command
if cmd:
    cmd.extend('drawBoxFromConf', lambda *args: drawBoxFromConf(*(
        [args[0]] + list(map(float,args[1:5])) + ([True] if args and args[-1] in ('dry', 'dry_run') else [False])
    )))

# CLI entry
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Draw box from conf file in PyMOL')
    parser.add_argument('conf_file')
    parser.add_argument('--lineWidth', type=float, default=2.0)
    parser.add_argument('--color', nargs=3, type=float, metavar=('R','G','B'), default=[1.0,1.0,1.0])
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    drawBoxFromConf(args.conf_file, args.lineWidth, *args.color, args.dry_run)
