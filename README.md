# espimg

Simple API to convert & serve images so that they can be used on E-Paper displays.

Selects & serves a random image from the `images/` directory over HTTP.

It begins by cutting the edges of the images to make them fit the display (removes e.g. white
background), then it optionally rotates the image to better fit the aspect ratio of the display.
Finally it converts the image to a grayscale 1bpp RAW image.

## Usage

Call the `/` endpoint to get a random image. For now the display size is hardcoded.
