import time
import sys
import logging
from logging.handlers import RotatingFileHandler
from getSongInfo import getSongInfo
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import sys,os
import configparser

def draw_clock_on_image(image):
    """Function to draw the current time (hours and minutes) at the bottom of an image."""
    draw = ImageDraw.Draw(image)

    # Load a font
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Update path if necessary
    font_size = 18  # Adjust size as needed
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    # Get the current time without seconds
    current_time = time.strftime("%H:%M", time.localtime())

    # Calculate width and height of the text to be drawn
    text_width, text_height = draw.textsize(current_time, font=font)
    
    # Calculate X, Y position of the text
    text_x = (image.width - text_width) // 2
    text_y = image.height - text_height - 5  # Position at the bottom with some padding
    
    # Draw the text
    draw.text((text_x, text_y), current_time, font=font, fill=(255, 255, 255))

    return image


if len(sys.argv) > 2:
    username = sys.argv[1]
    token_path = sys.argv[2]

    # Configuration file    
    dir = os.path.dirname(__file__)
    filename = os.path.join(dir, '../config/rgb_options.ini')

    # Configures logger for storing song data    
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='spotipy.log',level=logging.INFO)
    logger = logging.getLogger('spotipy_logger')

    # automatically deletes logs more than 2000 bytes
    handler = RotatingFileHandler('spotipy.log', maxBytes=2000,  backupCount=3)
    logger.addHandler(handler)

    # Configuration for the matrix
    config = configparser.ConfigParser()
    config.read(filename)

    options = RGBMatrixOptions()
    options.rows = int(config['DEFAULT']['rows'])
    options.cols = int(config['DEFAULT']['columns'])
    options.chain_length = int(config['DEFAULT']['chain_length'])
    options.parallel = int(config['DEFAULT']['parallel'])
    options.hardware_mapping = config['DEFAULT']['hardware_mapping']
    options.gpio_slowdown = int(config['DEFAULT']['gpio_slowdown'])
    options.brightness = int(config['DEFAULT']['brightness'])
    options.limit_refresh_rate_hz = int(config['DEFAULT']['refresh_rate'])

    default_image = os.path.join(dir, config['DEFAULT']['default_image'])
    print(default_image)
    matrix = RGBMatrix(options = options)

    prevSong    = ""
    currentSong = ""

    try:
      while True:
        try:
          imageURL = getSongInfo(username, token_path)[1]
          currentSong = imageURL

          if ( prevSong != currentSong ):
            response = requests.get(imageURL)
            image = Image.open(BytesIO(response.content))
            image.thumbnail((matrix.width, matrix.height), Image.Resampling.LANCZOS)
            matrix.SetImage(image.convert('RGB'))
            prevSong = currentSong

          time.sleep(1)
        except Exception as e:
          image = Image.open(default_image)
          image.thumbnail((matrix.width, matrix.height), Image.Resampling.LANCZOS)
          matrix.SetImage(image.convert('RGB'))
          print(e)
          time.sleep(1)
    except KeyboardInterrupt:
      sys.exit(0)

else:
    print("Usage: %s username" % (sys.argv[0],))
    sys.exit()