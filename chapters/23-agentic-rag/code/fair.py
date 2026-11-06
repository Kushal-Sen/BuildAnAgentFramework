"""Put chapter 20's best results beside this chapter's. It reads the output saved in chapter 20."""
from pathlib import Path

saved = Path("../../20-rag-pipeline/video")
print("Chapter 20, whole files with num_ctx 16384, all 42 questions:")
print((saved / "whole_files.txt").read_text().strip())
print("\nChapter 20, handbook pasted with num_ctx 8192, 32 handbook questions:")
print((saved / "eval_handbook.txt").read_text().strip())
