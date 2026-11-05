"""Provided: lets the exercises import whitebox from the code folder."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "code"))
