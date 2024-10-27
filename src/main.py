import tempfile
import random
from subprocess import Popen
from pathlib import Path
from fastapi import FastAPI
from PIL import Image
from fastapi.responses import FileResponse

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

def transform_picture(path: Path, width: int = 249, height = 122) -> Path:
    """ Transform the picture into a grayscale (black/white) 249x122 RAW format where each bit
    represents a pixel value (1/0). Automatically rotates the picture to best fit the aspect ratio """

    tmp_path = Path(tempfile.mktemp(suffix=path.suffix))
    print("tmp_path is", tmp_path);

    # Trim the image
    p = Popen(["magick", path, "-fuzz", "40%", "-trim", tmp_path])
    p.wait()


    # Rotate the image if it's taller than it is wide, so that it fits on a landscape screen
    # TODO: Make this respect the input width/height aspect ratio
    with Image.open(path) as img:
        img_w, img_h = img.size

    if img_h > img_w:
        print("rotating")
        p = Popen(["magick", tmp_path, "-rotate", "90", tmp_path])
        p.wait()

    options = [
        "magick",
        tmp_path,
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
        "1"
    ]

    # Perform transformation, print stdout
    p = Popen([*options, f"gray:{tmp_path.with_suffix('.raw')}"])
    p.wait()
    return tmp_path.with_suffix(".raw")

if __name__ == "__main__":
    transform_picture(Path("./images/anigirl.jpg"))
