"""Application entrypoint and compatibility shim.

This module serves as the main entry point for the geoflow application. It uses
`geoflow.ui.create_application` to build the PySide6 GUI application. It maintains
a small CLI compatibility surface and supports a `--headless` flag for automated
tests and CI environments where no GUI is needed.
"""

import sys
from typing import Sequence

try:
    # prefer the packaged UI
    from .ui import create_application
except Exception as e:
    raise ImportError("Failed to import geoflow.ui: " + str(e))


def main(argv: Sequence[str] | None = None) -> int:
    """Main entry point for the geoflow application.

    Parses command-line arguments, checks for the --headless flag, and initializes
    the PySide6 application. In headless mode, it returns immediately without
    starting the GUI event loop. Otherwise, it runs the application's event loop.

    Args:
        argv: Optional list of command-line arguments. If None, uses sys.argv[1:].

    Returns:
        int: Exit code (0 for success, or the result of app.exec() in GUI mode).
    """
    # Parse command-line arguments, defaulting to sys.argv[1:] if not provided
    argv = list(argv or sys.argv[1:])
    # Check for --headless flag to run without GUI (useful for tests and CI)
    headless = False
    if '--headless' in argv:
        headless = True
    # Create the PySide6 application and main window using the UI module
    app, win = create_application(argv=[sys.argv[0]] + argv, headless=headless)
    if headless:
        # In headless mode, return 0 immediately for headless test runs (no GUI loop)
        return 0
    # In GUI mode, start the application's event loop and return its exit code
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
