from pathlib import Path
import os

DEBUG=True
DATA_DIR=os.path.join(Path.home(), ".local", "share", "scout")

if DEBUG:
    DATA_DIR=os.path.join(Path.cwd(), "data")

def setup_data_dir():
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
