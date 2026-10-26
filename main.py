"""
Main Entry Point for DAA File Compression Tool.

Automatically launches the Tkinter Graphical User Interface (GUI) if available,
or drops into the Interactive Command-Line Menu (CLI) in terminal/headless environments.
Supports direct subcommands: compress, decompress, benchmark.
"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def main():
    # If explicit CLI flags or subcommands were provided
    if len(sys.argv) > 1:
        arg1 = sys.argv[1].lower()
        if arg1 in ("--web", "-w"):
            from server import launch_web_server
            launch_web_server()
            return
        elif arg1 in ("--gui", "-g"):
            from gui import launch_gui
            launch_gui()
            return
        elif arg1 in ("--cli", "-c"):
            from cli import interactive_menu
            interactive_menu()
            return
        else:
            # Delegate to CLI argument parser
            from cli import run_cli_arguments
            run_cli_arguments()
            return

    # No arguments provided: Attempt to launch GUI first
    try:
        import tkinter
        # Check if GUI window can be initialized (fails in headless/SSH without DISPLAY)
        from gui import launch_gui
        launch_gui()
    except (ImportError, tkinter.TclError) as e:
        # Graceful fallback to interactive CLI menu
        print(f"[Note] Graphical interface not available ({e}). Launching Interactive CLI Menu...")
        from cli import interactive_menu
        interactive_menu()


if __name__ == "__main__":
    main()
