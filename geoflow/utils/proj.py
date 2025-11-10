"""
Small projection utilities for geoflow using pyproj.

Functions:
- transform_points(src_crs, dst_crs, xs, ys) -> (xs2, ys2)
- wgs84_to_3857(xs, ys) convenience wrapper

Supports lists/tuples and numpy arrays (returns numpy arrays when numpy is present).
"""
from __future__ import annotations
from typing import Iterable, Tuple

try:
    from pyproj import Transformer
except Exception as e:
    raise ImportError('pyproj is required for geoflow.utils.proj: ' + str(e))

try:
    import numpy as np
except Exception:
    np = None


def transform_points(src_crs: str, dst_crs: str, xs: Iterable[float], ys: Iterable[float]) -> Tuple:
    """Transform point coordinates from src_crs to dst_crs.

    xs and ys can be lists/tuples or numpy arrays. Returns (xs2, ys2) with the
    same type (numpy arrays if numpy is installed).
    """
    transformer = Transformer.from_crs(src_crs, dst_crs, always_xy=True)
    if np is not None and isinstance(xs, (list, tuple)):
        xs = np.array(xs)
        ys = np.array(ys)
    if np is not None and isinstance(xs, np.ndarray):
        xs2, ys2 = transformer.transform(xs, ys)
        return xs2, ys2
    else:
        xs2 = []
        ys2 = []
        for x, y in zip(xs, ys):
            xx, yy = transformer.transform(x, y)
            xs2.append(xx)
            ys2.append(yy)
        return xs2, ys2


def wgs84_to_3857(xs, ys):
    """Convenience: WGS84 lon/lat -> Web Mercator (EPSG:3857)."""
    return transform_points('EPSG:4326', 'EPSG:3857', xs, ys)


if __name__ == '__main__':
    # small CLI
    import sys
    if len(sys.argv) < 3:
        print('Usage: python -m geoflow.utils.proj lon lat [lon lat ...]')
        sys.exit(1)
    vals = list(map(float, sys.argv[1:]))
    xs = vals[0::2]
    ys = vals[1::2]
    xs2, ys2 = wgs84_to_3857(xs, ys)
    for a, b in zip(xs2, ys2):
        print(a, b)
