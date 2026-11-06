"""Find video scenes that don't fit the stage, without recording anything.

usage: python check.py CHAPTER_DIR [CHAPTER_DIR ...]

Lays out every caption of every scene on the real stage and prints each one that runs
past its area. Prints nothing else for a chapter that fits. Exits 1 if anything doesn't.
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from record import HEIGHT, STAGE, WIDTH, load_scenes

MEASURE = """([scene, caption]) => {
  const MARGIN = 40;  // A long line can run into the right margin and still be read.
  document.querySelector("#scene").innerHTML = render[scene.type](scene);
  document.querySelector("#cap").textContent = caption.text;
  apply[scene.type](caption, scene);
  const area = document.querySelector("#scene").getBoundingClientRect();
  const cap = document.querySelector("#cap").getBoundingClientRect();
  const parts = [...document.querySelector("#scene").children].map((e) => e.getBoundingClientRect());
  const boxes = [...document.querySelectorAll(".code, .term")];
  return {
    top: area.top - Math.min(...parts.map((r) => r.top)),
    bottom: Math.max(...parts.map((r) => r.bottom)) - Math.min(area.bottom, cap.top),
    wide: Math.max(0, ...boxes.map((e) => e.scrollWidth - e.clientWidth - MARGIN)),
    clipped: Math.max(0, ...boxes.map((e) => e.scrollHeight - e.clientHeight)),
  };
}"""


def check(page, chapter):
    data = load_scenes(chapter)
    page.evaluate("text => { document.querySelector('#chapter').textContent = text; }", data["chapter"])
    bad = 0
    for number, scene in enumerate(data["scenes"], 1):
        for caption in scene["captions"]:
            size = page.evaluate(MEASURE, [scene, caption])
            over = {side: round(px) for side, px in size.items() if px > 1}
            if over:
                bad += 1
                print(f"{chapter.name} scene {number} {scene.get('output') or scene.get('file') or scene['type']}: "
                      f"{over} at \"{caption['text'][:50]}\"")
    return bad


def main():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT})
        page.goto(STAGE.as_uri())
        page.evaluate("document.fonts.ready.then(() => true)")
        bad = sum(check(page, Path(chapter)) for chapter in sys.argv[1:])
        browser.close()
    print(f"{bad} captions don't fit")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
