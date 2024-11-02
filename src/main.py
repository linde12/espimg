import random
import tempfile
from subprocess import call
from pathlib import Path
from subprocess import Popen

from fastapi import FastAPI
from fastapi.responses import FileResponse
from PIL import Image

app = FastAPI()


@app.get("/")
def generate_picture():
    pass
    picture_path = get_random_image()
    output_path = transform_picture(picture_path)
    # stream the image to the client
    return FileResponse(output_path)


def get_random_image():
    image_dir = Path("./images")
    images = list(image_dir.glob("*"))
    return random.choice(images)


def transform_picture(path: Path, width: int = 249, height: int = 122) -> Path:
    """Transform the picture into a grayscale (black/white) 249x122 RAW format where each bit
    represents a pixel value (1/0). Automatically rotates the picture to best fit the aspect ratio"""

    tmp_path = Path(tempfile.mktemp(suffix=path.suffix))
    print("tmp_path is", tmp_path)

    # Trim the image
    p = Popen(["magick", path, "-fuzz", "40%", "-trim", tmp_path])
    _ = p.wait()

    # Rotate the image if it's taller than it is wide, so that it fits on a landscape screen
    # TODO: Make this respect the input width/height aspect ratio
    with Image.open(tmp_path) as img:
        img_w, img_h = img.size

    if img_h > img_w:
        print("rotating")
        p = Popen(["magick", tmp_path, "-rotate", "90", tmp_path])
        _ = p.wait()

    # handle gifs, one file split by b'A' per frame - hack but works
    if path.suffix == ".gif":
        frames = get_frames(tmp_path)
        raw_frames = [convert_to_raw(frame, width, height) for frame in frames]
        return concat_gif(raw_frames)

    return convert_to_raw(tmp_path, width, height)


def convert_to_raw(path: Path, width: int, height: int) -> Path:
    options = [
        "magick",
        path,
        "-resize",
        f"{width}x{height}!",
        "-monochrome",
        "-background",
        "white",
        "-alpha",
        "remove",
        "-alpha",
        "off",
        "-depth",
        "1",
    ]

    # Perform transformation, print stdout
    p = Popen([*options, f"gray:{path.with_suffix('.raw')}"])
    _ = p.wait()
    return path.with_suffix(".raw")


def concat_gif(frames: list[Path]) -> Path:
    # condense the frames into a single file split by b'A'
    tmp = Path(tempfile.mktemp(suffix=".rawg"))
    tmp.touch()
    with open(tmp, "wb") as out:
        for idx, frame in enumerate(frames):
            is_last = idx == len(frames) - 1
            with open(frame, "rb") as inp:
                out.write(inp.read())
                if not is_last:
                    out.write(b"A")
    return tmp


def get_frames(path: Path) -> list[Path]:
    frames_path = Path(tempfile.mkdtemp(prefix="frames"))
    # convert gif to frames
    call(["magick", str(path), str(frames_path / "frame%04d.png")])
    return [*frames_path.glob("*.png")]
