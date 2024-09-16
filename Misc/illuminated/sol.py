from PIL import Image, ImageDraw

SIZE = 16
BLOCK_SIZE = 20
CHANNEL_MAX = 512

DMX0_CHANNEL_NB = 10*SIZE
DMX1_CHANNEL_NB =  8*SIZE

universe0 = list()
universe1 = list()
images = list()

def parse_file(filename):
    with open(filename, 'r') as f:
        for line in f:
            # Grab universe and DMX data
            [universe, dmx_data] = line.replace("\"", "").split(",")
            dmx_data = dmx_data.split(":")
            # Make sure we have universe 0 or 1
            # Also make sure we have data for the 512 DMX channels
            assert (universe == "0" or universe == "1")
            assert (len(dmx_data) == CHANNEL_MAX)
            # Update the corresponding sequence
            # ! Since there are two universes, a sequence is made of two chunks
            if universe == "0":
                universe0.append(dmx_data)
            else:
                universe1.append(dmx_data)

def draw_image(img, dmx, row_start, nb_channel):
    # Loop on DMX Channel
    for i in range(0, nb_channel*3, 3):
        # DMX channel
        ch = i // 3
        # Grab RGB colors
        rgb = (int(dmx[i], 16), int(dmx[i+1], 16), int(dmx[i+2], 16))
        # Draw the corresponding block in the image with the specified color
        row = row_start + ch // SIZE
        col = ch % SIZE
        if row % 2 != 0:
            # Odd row: right to left
            col = SIZE - col - 1
        rect = (col*BLOCK_SIZE, row*BLOCK_SIZE, (col+1)*BLOCK_SIZE, (row+1)*BLOCK_SIZE)
        draw = ImageDraw.Draw(img)
        draw.rectangle(rect, fill=rgb, outline=None)

def build_image(dmx0, dmx1):
    # Creates a new empty image
    img = Image.new('RGB', (SIZE*BLOCK_SIZE, SIZE*BLOCK_SIZE), (255, 255, 255))
    draw_image(img, dmx0, 0,  DMX0_CHANNEL_NB)
    draw_image(img, dmx1, 10, DMX1_CHANNEL_NB)
    return img

def build_images(n):
    for i in range(n):
        dmx0, dmx1 = universe0[i], universe1[i]
        img = build_image(dmx0, dmx1)
        images.append(img)

def build_gif(filename):
    images[0].save(filename,
                   save_all=True,
                   append_images=images[1:],
                   optimize=False,
                   duration=40, loop=0)

def main():
    parse_file('artnet.txt')
    # Make sure we have same amount of data for both universes
    assert len(universe0) == len(universe1)
    n = len(universe0)
    build_images(n)
    build_gif('artnet.gif')

main()
