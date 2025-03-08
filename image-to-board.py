import math
import numpy as np
from PIL import Image, ImageFile

class TooManyBombs(Exception):
    """Exception thrown when image has more than 256 bomb designated pixels"""
    def __init__(self, message ="Too many bombs found in image"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"TooManyBombsError: {self.message}"

def setup_image(image_relative_path: str,resize: tuple[float,float],threshold: int = 10) -> ImageFile.ImageFile:
    """
    Sets up the provided image for being used
    :param image_relative_path: The relative path from the script to find the file
    :param resize: Tuple for size to change image to if it is larger than this
    :param threshold: The threshold for what pixels turn black.
    :return: The setup image
    """
    img = Image.open(image_relative_path)
    print(f"Original Width {img.width} height: {img.height}")
    if img.mode != "RGB":
        img = img.convert("RGB")
    if img.size > resize:
        img.thumbnail(resize)
    black_and_white = img.point(lambda p: p > threshold and 255)
    return black_and_white

def create_mbf(img,reduce_if_over: bool,just_edge: bool):
    """
    Creates a regular mbf file for use in minesweeper programs. Uses already specified bomb pixel color
    :param img: The image to make mbf from
    :param reduce_if_over: If the number of bombs is greater than 255 try using the edge between white and black zones
    :param just_edge: If only the edge between white and black zones should become bombs
    :return: Nothing
    """
    name = img.filename.split(".")[0]
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
    if just_edge:
        bomb_indices = reduce_bomb_to_edge(pixels,width,height)
        num_bombs = len(bomb_indices)
    elif reduce_if_over and num_bombs > 256:
        reduced_indices = reduce_bomb_to_edge(pixels,width,height)
        if len(reduced_indices) <= 256 :
            bomb_indices = reduced_indices
            num_bombs = len(bomb_indices)
        else:
            raise TooManyBombs(f"Found {num_bombs} after reduction to just edges")


    print(f"Num bombs: {num_bombs}")

    mbf_list.append(math.floor(num_bombs / 256))
    mbf_list.append(num_bombs % 256)

    mbf_list += bomb_indices

    mbf_array = np.array(mbf_list, np.uint8)
    mbf_array.tofile(f"{name}.mbf")


def get_adjacent_value(pixels, x: int, y: int, width: int, height: int, dx: int, dy: int) -> int:
    """
    Gets the values of the adjacent pixels
    :param pixels: The pixels
    :param x: The x coord of pixel to find adjacent
    :param y: The y coord of pixel to find adjacent
    :param width: Total width of image
    :param height: Total height of image
    :param dx: The difference in x to check
    :param dy: The difference in y to check
    :return: The pixel values of the adjacent pixels.
    """
    nx, ny = x + dx, y + dy
    if nx < 0 or ny < 0 or nx >= width or ny >= height:
        return BOMB
    return pixels[nx, ny][0]

def reduce_bomb_to_edge(pixels, width: int, height: int) -> list[int]:
    """

    :param pixels: The pixels of the image
    :param width: The total width of image
    :param height: The total height of image
    :return: List of x then y coordinates for bombs
    """
    print("Reducing bombs")
    reduced_indices = []
    directions = [(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]

    for y in range(height):
        for x in range(width):
            try:
                cpixel = pixels[x, y][0]
                has_black_adjacent = any(get_adjacent_value(pixels, x, y, width, height, dx, dy) != BOMB for dx, dy in directions)
                if cpixel == BOMB and has_black_adjacent:
                    reduced_indices.append(x)
                    reduced_indices.append(y)
            except Exception as e:
                print(f"Error encountered at x: {x} and y: {y} {e}")

    return reduced_indices

try:
    filepath = "bad apple sample.bmp"
    BOMB = 255
    result = setup_image(filepath,(254,254),200)
    create_mbf(result,True,False)
except FileNotFoundError:
    print("Could not find image")
except Exception as e:
    print(f"An error occured: {e}")