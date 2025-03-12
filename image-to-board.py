import ast
import math
import random
import numpy as np
from PIL import Image, ImageFile
import argparse

class TooManyBombs(Exception):
    """Exception thrown when image has more than 256 bomb designated pixels"""
    def __init__(self, message ="Too many bombs found in image"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"Too Many Bombs Error: {self.message}"

class TooLargeImage(Exception):
    """Exception thrown when image dimmensions greater than 256x256"""
    def __init__(self, message ="Too many bombs found in image"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"Image Too Large Call with resize argument: {self.message}"

def setup_image(image_relative_path: str,resize: tuple[float,float],will_resize: bool,threshold: int = 10) -> ImageFile.ImageFile:
    """
    Sets up the provided image for being used
    :param image_relative_path: The relative path from the script to find the file
    :param resize: Tuple for size to change image to if it is larger than this
    :param threshold: The threshold for what pixels turn black.
    :return: The setup image
    """
    img = Image.open(image_relative_path)
    print(f"Original Width {img.width} height: {img.height}")

    if (not will_resize) and img.size > (254,254):
        raise TooLargeImage(f"Original Width {img.width} height: {img.height}")

    if img.mode != "RGB":
        img = img.convert("RGB")
    if will_resize and img.size > resize:
        img.thumbnail(resize)
    black_and_white = img.point(lambda p: p > threshold and 255)
    if(DEBUG and THRESHOLD_SET):
        black_and_white.show()
    return black_and_white

def create_mbf(name: str,img,reduce_if_over: bool,just_edge: bool,add_bombs: bool):
    """
    Creates a regular mbf file for use in minesweeper programs. Uses already specified bomb pixel color
    :param name: The name for the created mbf file
    :param img: The image to make mbf from
    :param reduce_if_over: If the number of bombs is greater than 255 try using the edge between white and black zones
    :param just_edge: If only the edge between white and black zones should become bombs
    :return: Nothing
    """
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
            if DEBUG:
                print(cpixel)
            assert cpixel[0] == 0 or cpixel[0] == 255, f"Found non 0 or 255 at {x} {y} found {cpixel[0]}"
            assert cpixel[1] == 0 or cpixel[1] == 255, f"Found non 0 or 255 at {x} {y} found {cpixel[1]}"
            assert cpixel[2] == 0 or cpixel[2] == 255, f"Found non 0 or 255 at {x} {y} found {cpixel[2]}"
            if cpixel[0] == BOMB:
                num_bombs += 1
                bomb_indices.append((x,y))
    if just_edge:
        bomb_indices = reduce_bomb_to_edge(pixels,width,height)
        if add_bombs:
            additional_bomb_count = get_num_additional_mines(width,height)
            additional_bombs = distribute_bombs(width,height,bomb_indices,additional_bomb_count)
            bomb_indices = bomb_indices + additional_bombs
    elif reduce_if_over and num_bombs > 256:
        print(f"Num bombs in image pre-reduction: {num_bombs}")
        reduced_indices = reduce_bomb_to_edge(pixels,width,height)
        if len(reduced_indices) <= 256 :
            bomb_indices = reduced_indices
        else:
            raise TooManyBombs(f"Found {num_bombs} after reduction to just edges")

    num_bombs = len(bomb_indices)
    print(f"Num bombs in image: {num_bombs}")

    mbf_list.append(math.floor(num_bombs / 256))
    mbf_list.append(num_bombs % 256)

    for _ in bomb_indices:
        mbf_list.append(_[0])
        mbf_list.append(_[1])

    is_aribiter_valid = num_bombs < 256 and height < 255 and width < 255

    mbf_array = np.array(mbf_list, np.uint8)
    mbf_array.tofile(f"{name}.mbf")
    print(f"MBF file {name}.mbf was created! Is Arbiter valid? {is_aribiter_valid}")

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

def reduce_bomb_to_edge(pixels, width: int, height: int) -> list[tuple[int,int]]:
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
                pixel = pixels[x, y][0]
                has_non_bomb_adjacent = any(get_adjacent_value(pixels, x, y, width, height, dx, dy) != BOMB for dx, dy in directions)
                if pixel == BOMB and has_non_bomb_adjacent:
                    reduced_indices.append((x,y))
            except Exception as e:
                print(f"Error encountered at x: {x} and y: {y} {e}")

    return reduced_indices

def distribute_bombs(width: int, height: int, edges: list[tuple[int,int]], num_bombs: int) -> list[tuple[int,int]]:
    """
    :param width: The width of the board
    :param height: The height of the board
    :param edges: The already placed bomb edges
    :param num_bombs: The number of bombs to distribute
    :return: List of x,y coordinates for bombs
    """
    directions = [(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]
    possible_points = []
    for x in range(width):
        for y in range(height):
            if edges.count((x,y)) == 0 and not any(has_edge_adjacent(x,y,dx,dy,edges) for dx,dy in directions):
                possible_points.append((x,y))
    random.shuffle(possible_points)
    return possible_points[:num_bombs]


def has_edge_adjacent(x:int, y:int,dx: int, dy: int, edges: list[tuple[int,int]]) -> bool:
    """
    Checks if there is an already placed edge bomb adjacent
    :param x: The x coordinate
    :param y: The y coordinate
    :param dx: The difference in x to check
    :param dy: The difference in y to check
    :param edges: The already existing edges
    :return: If there is an edge adjacent to this position
    """
    nx, ny = x + dx, y + dy
    return bool(edges.count((nx,ny)))

def get_num_additional_mines(width:int, height: int)->int:
    if width >= 30 and height >= 16:
        return math.floor((width * height) * 0.20)
    elif width >= 16 and height >= 16:
        return math.floor((width * height) * 0.15)
    else:
        return math.floor((width * height) * 0.12)

parser = argparse.ArgumentParser("Image To Minesweeper Board",
                                 "Converts images to mfb files that can be loaded by minesweeper programs like Arbiter or JSMinesweeper")
parser.add_argument("-f","--File",help= "Path to the file to convert", required=True)
parser.add_argument("-c","--Color",help="black or white (case insensitive), the color that should become bombs in the board", required=True)
parser.add_argument("-r","--Resize",help="Dimmensions to resize image to (width,height), (254,254) to work with arbiter.", required=False)
parser.add_argument("-re","--ReduceBombs",help= "If the script should try to be limited to 255 bombs. If above try to use edges only. Do not use with Edge option", action="store_true",required=False)
parser.add_argument("-e","--Edge",help="If the script should make board based of edges between white and black areas. Do not use with ReduceBombs option",action="store_true",required=False)
parser.add_argument("-d","--Debug",help="Run the script in debug mod and gett more logging. Will show image if threshold value is set.",action="store_true",required=False)
parser.add_argument("-t","--Threshold",help="Threshold value for images for if pixel should be black or white. Use if image is not showing as desired. Use debug to see result.",required=False)
parser.add_argument("-n","--Name",help="The name of the created mbf file.",required=False)
parser.add_argument("-a","--AddBombs",help="Adds additional bombs randomly to board to make it more enjoyable.",action="store_true",required=False)
args = parser.parse_args()

DEBUG = args.Debug
THRESHOLD_SET = False

try:
    filepath = args.File

    BOMB = 255
    if args.Color.lower() == 'black' or args.Color == 0 :
        BOMB = 0

    will_resize_arg = True
    resize_arg = args.Resize
    if args.Resize is None:
        resize_arg = (255, 255)
        will_resize_arg = False
    else:
        resize_arg = ast.literal_eval(args.Resize)

    if args.Threshold is None:
        threshold_arg = 200
    else:
        threshold_arg = int(args.Threshold)
        THRESHOLD_SET = True

    if args.Name is None:
        args.Name = filepath.split(".")[0]

    if args.AddBombs is None:
        args.AddBombs = False

    result = setup_image(filepath,resize_arg,will_resize_arg,threshold_arg)
    create_mbf(args.Name,result,args.ReduceBombs,args.Edge,args.AddBombs)
except FileNotFoundError:
    print("Could not find image")
except Exception as e:
    print(f"An error occured: {e}")