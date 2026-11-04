"""Record a silent, captioned chapter video from its video/scenes.json.

usage: python record.py CHAPTER_DIR OUT_DIR

Needs: pip install -r tools/video/requirements.txt, then: python -m playwright install chromium
Writes OUT_DIR/video.mp4 and a screenshot for each caption marked "shot" in the script.
Code and terminal scenes read the chapter's real files, so re-record after they change.
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import imageio_ffmpeg
from playwright.sync_api import sync_playwright

WIDTH, HEIGHT = 1440, 900
STAGE = Path(__file__).parent / "stage.html"


def load_scenes(chapter):
    data = json.loads((chapter / "video" / "scenes.json").read_text())
    for scene in data["scenes"]:
        if "file" not in scene:
            continue
        lines = (chapter / scene["file"]).read_text().splitlines()
        if scene["type"] == "code":
            first = next(i for i, line in enumerate(lines) if scene["start"] in line)
            last = next(i for i, line in enumerate(lines) if i > first and scene["end"] in line)
            lines = lines[first:last + 1]
        scene["lines"] = lines
    return data


def record(chapter, out):
    data = load_scenes(chapter)
    length = sum(c["secs"] for scene in data["scenes"] for c in scene["captions"])
    raw = out / "raw"
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(
            viewport={"width": WIDTH, "height": HEIGHT},
            record_video_dir=str(raw),
            record_video_size={"width": WIDTH, "height": HEIGHT},
        )
        page = context.new_page()
        opened = time.time()
        page.goto(STAGE.as_uri())
        page.evaluate("document.fonts.ready.then(() => true)")
        lead = time.time() - opened
        page.evaluate("data => { window.start(data); }", data)
        while not page.evaluate("window.__done === true"):
            shot = page.evaluate("const s = window.__shot; window.__shot = null; s")
            if shot:
                page.screenshot(path=str(out / f"{shot}.jpg"), type="jpeg", quality=85)
            time.sleep(0.2)
        webm = page.video.path()
        context.close()
        browser.close()
    subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-ss", f"{lead:.2f}",
         "-i", str(webm), "-t", str(length), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "24",
         "-movflags", "+faststart", str(out / "video.mp4")],
        check=True,
    )
    shutil.rmtree(raw)


if __name__ == "__main__":
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    record(Path(sys.argv[1]), out_dir)
