#!/usr/bin/env python3
"""
Sky Simulator Launcher
This script starts the interactive Sky Simulator GUI application.
"""

import sys
import os

# Add the current directory to Python path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from sky_simulator_gui import main
    print("Starting Sky Simulator GUI...")
    main()
except ImportError as e:
    print(f"Error: Could not import sky_simulator_gui.py - {e}")
    print("Make sure sky_simulator_gui.py is in the same directory as this script.")
    sys.exit(1)
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)