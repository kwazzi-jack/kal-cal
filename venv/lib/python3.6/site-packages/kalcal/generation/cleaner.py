import shutil
import os


def ms(path):
    """Remove measurement set if it is 
    in dataset, otherwise move on."""

    breakdown = path.split('.')
    if breakdown[-1] != 'MS':
        print(f"Folder {path} is not an MS.")
    else:
        try:
            shutil.rmtree(path)
            print(f"Removed folder {path}.")
        except:
            print(f"Folder {path} does not exist.")


def gains(path):
    """Remove gains-file if it is 
    in dataset, otherwise move on."""

    breakdown = path.split('.')
    if breakdown[-1] != 'npy':
        print(f"File {path} is not a .npy file.")
    else:
        try:
            os.remove(path)
            print(f"Removed folder {path}.")
        except:
            print(f"File {path} does not exist.")