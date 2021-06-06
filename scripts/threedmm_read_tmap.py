from PIL import Image, ImageDraw

ORDER_LITTLE = 'little'
IMAGE_BACKGROUND_COLOR = (255,255,255,0)

# Path to GLCR file.
path_palette = "<insert path here>"

# Path to TMAP file.
path_tmap = "<insert path here>"

with open(path_palette, 'rb') as file_palette:
    data_palette = file_palette.read()

channel_count = int.from_bytes(data_palette[4:8], byteorder=ORDER_LITTLE, signed=False)
colour_count = int.from_bytes(data_palette[8:12], byteorder=ORDER_LITTLE, signed=False)

colours = []

for i in range(colour_count):
    start = 12 + i*4
    blue = int.from_bytes(data_palette[start:start+1], byteorder=ORDER_LITTLE, signed=False)
    green = int.from_bytes(data_palette[start+1:start+2], byteorder=ORDER_LITTLE, signed=False)
    red = int.from_bytes(data_palette[start+2:start+3], byteorder=ORDER_LITTLE, signed=False)
    alpha = int.from_bytes(data_palette[start+3:start+4], byteorder=ORDER_LITTLE, signed=False)

    colours.append((red, green, blue))

with open(path_tmap, 'rb') as file_tmap:
    data_tmap = file_tmap.read()

width = int.from_bytes(data_tmap[12:14], byteorder=ORDER_LITTLE, signed=False)
height = int.from_bytes(data_tmap[14:16], byteorder=ORDER_LITTLE, signed=False)

print("Width: " + str(width) + ", height: " + str(height))

pixel_count = width * height

texture_image = Image.new('RGB', (width, height), color = IMAGE_BACKGROUND_COLOR)
texture_draw = ImageDraw.Draw(texture_image)

for x in range(width):
    for y in range(height):
        address = 20 + x + width*y

        palette_index = int.from_bytes(data_tmap[address:address+1], byteorder=ORDER_LITTLE, signed=False)
        colour = colours[palette_index]

        texture_draw.point((x, height - 1 - y), fill = colour)

texture_image.save("out.png", "PNG")
