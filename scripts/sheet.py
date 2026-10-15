"""Dev aid: snapshot several SVGs and stack them into one contact sheet (preview/sheet.png)."""
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from snap import snapshots

args = sys.argv[1:]
t = float(args.pop(0)); mode = args.pop(0)
bg = "#0D1117" if mode == "dark" else "#FFFFFF"
imgs = []
for i, a in enumerate(args):
    out = Path("preview") / f"_s{i}.png"
    out.parent.mkdir(exist_ok=True)
    snapshots(Path(a), [t], [out], scheme=mode, bg=bg)
    imgs.append(Image.open(out).convert("RGB"))
W = max(i.width for i in imgs)
H = sum(i.height + 10 for i in imgs)
sheet = Image.new("RGB", (W, H), bg)
y = 0
for i in imgs:
    sheet.paste(i, (0, y)); y += i.height + 10
sheet.save("preview/sheet.png")
print(sheet.size)
