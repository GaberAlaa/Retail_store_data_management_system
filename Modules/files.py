import shutil
from Modules import config

def copy_to_raw(file_path ):
    destination = config.RAW_FOLDER / file_path.name
    shutil.copy(file_path, destination)
 

def move_to_processed(file_path):
    destination = config.PROCESSED_FOLDER / file_path.name
    shutil.move(file_path, destination)
    return destination
 
 
def move_to_rejected(file_path):
    destination = config.REJECTED_FOLDER / file_path.name
    shutil.move(file_path, destination)
    return destination

