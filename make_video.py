import asyncio
import re
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import edge_tts

ROOT = Path(__file__).parent
OUT = ROOT / "output"
SCRIPT = OUT / "script.md"
VOICE = "en-US-AriaNeural"
W, H = 1920, 1080

def get_font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for name in candidates:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()

def clean_script(text):
    text = re.sub(r"^#.*$", "", text, flags=re.M)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    return text.strip()

def chunks_from_script(text, max_words=85):
    paragraphs = [p.strip() for p in text.splitlines() if p.strip()]
    chunks, current = [], []
    count = 0
    for para in paragraphs:
        words = para.split()
        if count + len(words) > max_words and current:
            chunks.append(" ".join(current))
            current, count = [], 0
        current.extend(words)
        count += len(words)
    if current:
        chunks.append(" ".join(current))
    return chunks or ["Welcome to our product review."]

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, line = [], ""
    for word in words:
        trial = (line + " " + word).strip()
        if draw.textbbox((0, 0), trial, font=font)[2] <= max_width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def make_slide(index, total, title, text, path):
    img = Image.new("RGB", (W, H), (12, 24, 43))
    px = img.load()
    # Subtle original gradient; no external image assets.
    for y in range(H):
        t = y / H
        color = (int(12 + 5*t), int(24 + 24*t), int(43 + 30*t))
        for x in range(W):
            px[x, y] = color
    draw = ImageDraw.Draw(img)
    title_font = get_font(64, True)
    body_font = get_font(43)
    small_font = get_font(28)
    draw.rounded_rectangle((100, 90, W-100, H-90), radius=36, outline=(57, 107, 133), width=3)
    draw.text((150, 135), "BRAIN HEALTH REVIEW LAB", font=small_font, fill=(111, 208, 198))
    draw.text((150, 205), title[:90], font=title_font, fill=(245, 248, 252))
    lines = wrap_text(draw, text, body_font, W-320)
    y = 360
    for line in lines[:9]:
        draw.text((155, y), line, font=body_font, fill=(218, 228, 239))
        y += 72
    draw.text((150, H-155), "EDUCATIONAL REVIEW • VERIFY PRODUCT DETAILS BEFORE PURCHASE",
              font=small_font, fill=(145, 170, 190))
    draw.text((W-260, H-155), f"{index+1:02d} / {total:02d}",
              font=small_font, fill=(111, 208, 198))
    img.save(path, quality=92)

async def create_voice(text, target):
    communicate = edge_tts.Communicate(text, VOICE, rate="-3%", volume="+0%")
    await communicate.save(str(target))

def run(cmd):
    subprocess.run(cmd, check=True)

def main():
    if not SCRIPT.exists():
        raise SystemExit("Missing output/script.md. Run the script-generation workflow first.")
    raw = SCRIPT.read_text(encoding="utf-8")
    text = clean_script(raw)
    if len(text.split()) < 250:
        raise SystemExit("Script is too short for video production. Review output/script.md.")
    OUT.mkdir(exist_ok=True)
    audio = OUT / "narration.mp3"
    asyncio.run(create_voice(text, audio))

    title_match = re.search(r"^#\s+(.+)$", raw, flags=re.M)
    title = title_match.group(1).strip() if title_match else "Phytomem One Review"
    chunks = chunks_from_script(text)
    slide_dir = OUT / "slides"
    slide_dir.mkdir(exist_ok=True)
    slides_txt = OUT / "slides.txt"
    # Estimate scene duration by word count; final duration is clipped to narration.
    total_words = sum(len(c.split()) for c in chunks)
    with slides_txt.open("w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks):
            image_path = slide_dir / f"slide_{i:03d}.png"
            make_slide(i, len(chunks), title if i == 0 else f"Review: {title}", chunk, image_path)
            duration = max(5, 180 * len(chunk.split()) / total_words)
            f.write(f"file '{image_path.as_posix()}'\n")
            f.write(f"duration {duration:.3f}\n")
        # concat demuxer needs the final image repeated to honor its duration
        last = slide_dir / f"slide_{len(chunks)-1:03d}.png"
        f.write(f"file '{last.as_posix()}'\n")

    video = OUT / "video.mp4"
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(slides_txt),
        "-i", str(audio), "-vf", "scale=1920:1080,format=yuv420p",
        "-c:v", "libx264", "-preset", "ultrafast", "-r", "25",
        "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart",
        str(video)
    ])
    print(f"Created {video}")

if __name__ == "__main__":
    main()
