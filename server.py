"""
Author: Yonathan Chapal
Program name: Exc 2.7
Description: a basic commands server
Date: 10/11/2023
"""

import socket
import glob
import os


def get_file_list(path):
    # make sure the path is in valid format for glob search
    path = path.replace("/", "\\")
    files = glob.glob(rf"{path}/*.*", recursive=False)

    # change format back to /
    for i in range(len(files)):
        files[i] = files[i].replace("\\", "/")

    return files


def delete_file(path):
    # make sure the path is using only /
    path = path.replace("\\", "/")
    try:
        os.remove(path)
        # signal removal as successful
        return 0
    except OSError as err:
        print("file is a directory!")
        return err.args[0] # Errno 13
    except FileNotFoundError as err:
        print("no such file exists")
        return err.args[0] # Errno 2


def copy_file(src, dest):
    # make sure the paths is using only /
    src = src.replace("\\", "/")
    dest = dest.replace("\\" "/")
