"""
Small helper to generate a synthetic SEG-Y file for tests.

Behavior:
- Prefer `segyio` if importable: use it to write a proper SEG-Y file.
- Otherwise, write a minimal-but-usable SEG-Y file using pure Python: 3200-byte EBCDIC/text header, 400-byte binary header, and X traces with simple float32 samples.

The generated file will be written to `tests/data/seismic.sgy` relative to the project root.
"""
from __future__ import annotations
import os
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / 'tests' / 'data'
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / 'seismic.sgy'


def generate_with_segyio(path: Path, n_traces=10, n_samples=256, dt_us=4000):
    import numpy as np
    import segyio

    # Create simple synthetic traces: a delayed Ricker-like pulse per trace
    samples = np.linspace(0, (n_samples - 1) * dt_us * 1e-6, n_samples)
    data = np.zeros((n_traces, n_samples), dtype=np.float32)
    for i in range(n_traces):
        t0 = 0.05 + i * 0.001
        freq = 25.0
        # Ricker-like
        pi = np.pi
        a = (1 - 2 * (pi * freq * (samples - t0))**2) * np.exp(-(pi * freq * (samples - t0))**2)
        data[i, :] = a.astype(np.float32)

    spec = {
        'samples': (0, n_samples - 1),
        'format': 'FLOAT',
        'tracecount': n_traces,
    }

    # segyio requires a template; easiest is to use segyio.writer
    with segyio.create(str(path), spec) as f:
        # set binary header sample interval in microseconds
        f.bin[segyio.BinField.Interval] = dt_us
        for it in range(n_traces):
            f.trace[it] = data[it, :]
            # set some header fields
            tr = f.header[ it ]
            tr[segyio.TraceField.TRACE_SEQUENCE_LINE] = it + 1
    print('Wrote SEG-Y with segyio:', path)


def generate_minimal(path: Path, n_traces=10, n_samples=256, dt_us=4000):
    """Write a minimal SEG-Y-like file (not fully spec compliant but readable by many readers).

    Layout:
    - 3200 bytes: textual header (ASCII, padded)
    - 400 bytes: binary header
    - n_traces * (240-byte trace header + n_samples * 4 bytes float32 samples)
    """
    import numpy as np

    text_header = ("C 1 CLIENT                        COMPANY  " + " " * 3180)[:3200]
    # binary header: we'll set sample interval and number of samples at specific offsets
    # To keep it simple we zero-fill and pack sample interval (2 bytes at offset 16) and num samples (2 bytes at 20)
    bin_header = bytearray(400)
    # sample interval (microseconds) at bytes 16-17 as int16
    bin_header[16:18] = struct.pack('>h', int(dt_us))
    # number of samples per trace at bytes 20-21 as int16
    bin_header[20:22] = struct.pack('>h', int(n_samples))

    # generate data
    samples = np.linspace(0, (n_samples - 1) * dt_us * 1e-6, n_samples)
    data = np.zeros((n_traces, n_samples), dtype=np.float32)
    for i in range(n_traces):
        t0 = 0.05 + i * 0.001
        freq = 25.0
        pi = np.pi
        a = (1 - 2 * (pi * freq * (samples - t0))**2) * np.exp(-(pi * freq * (samples - t0))**2)
        data[i, :] = a.astype(np.float32)

    with open(path, 'wb') as f:
        f.write(text_header.encode('ascii'))
        f.write(bin_header)
        for it in range(n_traces):
            # 240-byte trace header (mostly zeros). We'll set sample count at bytes 114-115 (2 bytes) big-endian
            th = bytearray(240)
            th[114:116] = struct.pack('>h', int(n_samples))
            f.write(th)
            f.write(data[it, :].astype('>f4').tobytes())
    print('Wrote minimal SEG-Y:', path)


if __name__ == '__main__':
    # try segyio
    try:
        import segyio  # type: ignore
        print('segyio available; using segyio writer')
        generate_with_segyio(OUT_FILE)
    except Exception as e:
        print('segyio not usable (', type(e).__name__, str(e), '), falling back to minimal writer')
        generate_minimal(OUT_FILE)

    st = OUT_FILE.stat()
    print('Generated:', OUT_FILE, 'size=', st.st_size)
