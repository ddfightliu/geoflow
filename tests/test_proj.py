import math
from geoflow.utils.proj import wgs84_to_3857


def test_wgs84_to_3857_single():
    # Known coordinate: lon=0,lat=0 => x=0,y=0 in Web Mercator
    x, y = wgs84_to_3857([0], [0])
    # returns numpy arrays or lists; normalize
    if hasattr(x, 'item'):
        x = float(x[0])
        y = float(y[0])
    else:
        x = x[0]
        y = y[0]
    assert abs(x) < 1e-6
    assert abs(y) < 1e-6


def test_wgs84_to_3857_batch():
    lons = [0, 116.39139]
    lats = [0, 39.9075]
    xs, ys = wgs84_to_3857(lons, lats)
    # basic sanity checks
    if hasattr(xs, 'tolist'):
        xs = xs.tolist(); ys = ys.tolist()
    assert len(xs) == 2
    # second point should have non-zero x/y
    assert abs(xs[1]) > 1
    assert abs(ys[1]) > 1
