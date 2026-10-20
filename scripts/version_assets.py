"""Version homepage CSS and JavaScript URLs by their contents before deployment."""
import hashlib
import re
from pathlib import Path


def main():
    dist = Path(__file__).resolve().parents[1] / "dist"
    page = dist / "index.html"
    html = page.read_text(encoding="utf-8")
    for name in ("style.css", "snow.js"):
        version = hashlib.sha256((dist / name).read_bytes()).hexdigest()[:12]
        pattern = rf'((?:href|src)="){re.escape(name)}(?:\?[^"]*)?(")'
        html, count = re.subn(
            pattern, lambda match: f'{match[1]}{name}?v={version}{match[2]}', html
        )
        if count != 1:
            raise ValueError(f"Expected one homepage reference to {name}, found {count}")
    page.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
