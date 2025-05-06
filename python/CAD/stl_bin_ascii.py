"""""
Convert STL Binary to ASCII Format

This script converts a binary STL file to an ASCII STL file using the numpy-stl library.

Usage:
    python convert_stl.py input_binary.stl output_ascii.stl

Example:
    python convert_stl.py model_binary.stl model_ascii.stl
"""

import sys
from stl import mesh

if len(sys.argv) != 3:
    print("Usage: python convert_stl.py input_binary.stl output_ascii.stl")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

m = mesh.Mesh.from_file(input_file)
m.save(output_file, mode=mesh.stl.Mode.ASCII)

