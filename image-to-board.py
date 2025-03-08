import math
import numpy as np
from PIL import Image, ImageFile

def setup_image(image_relative_path: str,resize: tuple[float,float],threshold: int = 10) -> ImageFile.ImageFile:
    img = Image.open(image_relative_path)
    print(f"Original Width {img.width} height: {img.height}")
    if img.mode != "RGB":
        img = img.convert("RGB")
    if img.size > resize:
        img.thumbnail(resize)
    black_and_white = img.point(lambda p: p > threshold and 255)
    return black_and_white

def create_mbf(img,reduce_if_over: bool,name: str):
    pixels = img.load()
    mbf_list = []
    height = img.height
    width = img.width
    mbf_list.append(width)
    mbf_list.append(height)

    num_bombs = 0
    bomb_indices = []
    for y in range(height-1):
        for x in range(width-1):
            try:
                cpixel = pixels[x, y]
            except Exception as e:
                print(f"Error on x:{x} y:{y} {e} width: {width} height {height}")
            print(cpixel)
            assert cpixel[0] == 0 or cpixel[0] == 255, f"Found non 0 or 255 at {x} {y} found {cpixel[0]}"
            assert cpixel[1] == 0 or cpixel[1] == 255, f"Found non 0 or 255 at {x} {y} found {cpixel[1]}"
            assert cpixel[2] == 0 or cpixel[2] == 255, f"Found non 0 or 255 at {x} {y} found {cpixel[2]}"
            if cpixel[0] == BOMB:
                num_bombs += 1
                bomb_indices.append(x)
                bomb_indices.append(y)
    print(f"Num bombs in image: {num_bombs}")
    if reduce_if_over and num_bombs > 256:
        bomb_indices = reduce_bomb_to_edge(pixels,width,height)
        num_bombs = len(bomb_indices)

    print(f"Num bombs: {num_bombs}")

    mbf_list.append(math.floor(num_bombs / 256))
    mbf_list.append(num_bombs % 256)

    mbf_list += bomb_indices

    mbf_array = np.array(mbf_list, np.uint8)
    mbf_array.tofile(f"{name}.mbf")


def reduce_bomb_to_edge(pixels,width: int,height: int) -> []:
    print("Reducing bombs")
    reduced_indices = []
    for y in range(height):
        for x in range(width):
            try:
                pixel = pixels[x, y]
                left_up = BOMB if y == 0 or x == 0 else pixels[x-1,y-1][0]
                up = BOMB if y == 0 else pixels[x,y-1][0]
                right_up = BOMB if y == 0 or x == width-1 else pixels[x+1,y-1][0]
                right = BOMB if x == width-1 else pixels[x+1,y][0]
                right_down = BOMB if x == width-1 or y == height-1 else pixels[x+1,y+1][0]
                down = BOMB if y == height-1 else pixels[x,y+1][0]
                left_down = BOMB if y== height-1 or x == 0 else pixels[x-1,y+1][0]
                left = BOMB if x == 0 else pixels[x-1,y][0]
                has_black_adjacent = left_up != BOMB or up != BOMB or right_up != BOMB
                has_black_adjacent = has_black_adjacent or right_up != BOMB or right != BOMB or right_down != BOMB
                has_black_adjacent = has_black_adjacent or down != BOMB or left_down != BOMB or left != BOMB
                if pixel[0] == BOMB and has_black_adjacent:
                    reduced_indices.append(x)
                    reduced_indices.append(y)
            except Exception as e:
                print(f"Error encountered at x: {x} and y:{y} {e}")
        return reduced_indices

try:
    filepath = "mario.bmp"
    BOMB = 255
    result = setup_image(filepath,(254,254),200)
    create_mbf(result,True,filepath.split(".")[0])
except FileNotFoundError:
    print("Could not find image")
except Exception as e:
    print(f"An error occured: {e}")