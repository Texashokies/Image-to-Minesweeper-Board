# Image to mine sweeper board
Python script that converts a black and white image to a playable minesweeper board.

The best images are already only in black (0,0,0) and white (255,255,255) and originally size 255x255 or smaller.

Images that are not only black or white will be converted using pillow's point method with a threshold that can be 
configured by argument.

Images larger than 256 x 256 will be scaled down to 254 width preserving aspect ratio.

# Set up
Need python 3 installed, run pip install -r requirements.txt

# Running the script
`python image-to-board.py --help` Get list of arguments and how to use

`python image-to-board.py --File "mario.bmp" --Color black` 

# Using MBF File

The MBF file can be loaded as a custom board for https://minesweepergame.com/download/arbiter.php if board size is 255x255 and has 255 bombs or less.

The script should inform you if the generated board is compatible with Arbiter. 
If even after resizing to under 256x256 try the ReduceBombs argument to get under 256 bombs.

Otherwise, MBF files can be used with JSMinesweeper or it's forks by dragging the mbf file onto the board:

* https://github.com/DavidNHill/JSMinesweeper at https://davidnhill.github.io/JSMinesweeper/
* https://github.com/nineteendo/JSMinesweeper at https://nineteendo.github.io/JSMinesweeper/
