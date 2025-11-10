"""bench_pyvista_heavy.py

Creates a heavier mixed scene (point cloud + isosurfaces), runs a short headless
render loop to measure average FPS and prints metrics. For interactive mode, pass
--interactive to open a window instead of headless timed run.

Usage:
  python tests/bench_pyvista_heavy.py        # headless 5s run
  python tests/bench_pyvista_heavy.py --interactive --points 200000
"""
import time
import argparse
import numpy as np
import pyvista as pv


def make_scene(n_points=200_000, grid_n=80):
    pts = np.random.uniform(-1, 1, size=(n_points, 3)).astype('float32')
    point_cloud = pv.PolyData(pts)

    x = np.linspace(-1.2, 1.2, grid_n)
    y = np.linspace(-1.2, 1.2, grid_n)
    z = np.linspace(-1.2, 1.2, grid_n)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    scalars = np.exp(-((X - 0.3) ** 2 + (Y + 0.2) ** 2 + (Z * 1.0) ** 2) * 8.0) + \
              0.6 * np.exp(-((X + 0.4) ** 2 + (Y - 0.3) ** 2 + (Z * 0.8) ** 2) * 12.0)

    # Some pyvista versions may not expose UniformGrid; construct a StructuredGrid
    # Create points for StructuredGrid
    nx, ny, nz = scalars.shape
    pts_coords = np.column_stack((X.ravel(), Y.ravel(), Z.ravel()))
    sgrid = pv.StructuredGrid()
    sgrid.points = pts_coords
    sgrid.dimensions = scalars.shape
    # attach scalars as point data
    sgrid.point_data['values'] = scalars.ravel(order='F')

    iso = sgrid.contour(isosurfaces=3)
    return point_cloud, iso


def run_headless(n_points=200_000, grid_n=80, seconds=5):
    point_cloud, iso = make_scene(n_points=n_points, grid_n=grid_n)
    p = pv.Plotter(off_screen=True)
    t0 = time.perf_counter()
    p.add_mesh(iso, color='orange', opacity=0.5)
    # use extract_all_edges for broader compatibility
    try:
        edges = iso.extract_edges()
    except Exception:
        edges = iso.extract_all_edges()
    p.add_mesh(edges, color='black', line_width=0.2)
    p.add_points(point_cloud, render_points_as_spheres=False, point_size=2, color='white')
    t1 = time.perf_counter()
    print(f'PyVista HEADLESS: prepare+add scene: {t1 - t0:.3f}s (n points={n_points}, grid={grid_n})')

    # warmup renders
    for _ in range(3):
        p.render()

    frames = 0
    start = time.perf_counter()
    now = start
    while now - start < seconds:
        p.render()
        frames += 1
        now = time.perf_counter()
    elapsed = now - start
    avg_fps = frames / elapsed if elapsed > 0 else 0.0
    print(f'Headless average FPS over {elapsed:.2f}s: {avg_fps:.2f} (frames={frames})')


def run_interactive(n_points=100000000_1200000000, grid_n=20000000000):
    point_cloud, iso = make_scene(n_points=n_points, grid_n=grid_n)
    p = pv.Plotter(off_screen=False)
    p.add_mesh(iso, color='orange', opacity=0.5)
    try:
        edges = iso.extract_edges()
    except Exception:
        edges = iso.extract_all_edges()
    p.add_mesh(edges, color='black', line_width=0.2)
    p.add_points(point_cloud, render_points_as_spheres=True, point_size=3, color='white')
    # add FPS label updated by callback
    #txt = p.add_text('FPS: --', position='upper_left')

    # Show window non-blocking and update FPS in a manual render loop.
    p.show(auto_close=False)
    last_time = time.perf_counter()
    frames = 0
    try:
        while True:
            p.camera.Azimuth(0.2)
            p.render()
            frames += 1
            now = time.perf_counter()
            if now - last_time >= 0.5:
                fps = frames / (now - last_time)
                p.add_text(f'FPS: {fps:.1f}', name='fps_text', position='upper_left', font_size=12, color='white')
                frames = 0
                last_time = now
            print(fps)
    except Exception:
        # window closed or error occurred
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # default: interactive UI; use --headless to run timed headless benchmark
    parser.add_argument('--headless', action='store_true', help='Run headless timed benchmark (no UI)')
    parser.add_argument('--points', type=int, default=200000)
    parser.add_argument('--grid', type=int, default=80)
    parser.add_argument('--seconds', type=float, default=5.0)
    args = parser.parse_args()

    if args.headless:
        run_headless(n_points=args.points, grid_n=args.grid, seconds=args.seconds)
    else:
        run_interactive(n_points=args.points, grid_n=args.grid)
