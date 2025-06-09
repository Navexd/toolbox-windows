import os
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(__file__)

STYLESHEET_PATH = os.path.join(BASE_DIR, "styles.qss")
IMAGES_DIR = os.path.join(BASE_DIR, "pick")
