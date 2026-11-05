"""Provided: lets the exercises find the whitebox package inside code/."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "code"))
