"""
Author: Yonathan Chapal
Program name: Exc 2.7
Description: A basic commands server
Date: 10/11/2023
"""

import socket
import glob
import os
import shutil
import subprocess
from PIL import ImageGrab


def get_file_list(path):
    """
    Get the list of files in the specified directory.

    :param path: The path of the directory.
    :type path: str

    :return: A list of file paths in the directory.
    :rtype: list
    """
    # Ensure the path is in a valid format for glob search
    path = path.replace("/", "\\")
    files = glob.glob(rf"{path}/*.*", recursive=False)

    # Change format back to /
    for i in range(len(files)):
        files[i] = files[i].replace("\\", "/")

    return files


def delete_file(path):
    """
    Delete a file at the specified path.

    :param path: The path of the file to be deleted.
    :type path: str

    :return: 0 if successful, error code otherwise.
    :rtype: int
    """
    # Ensure the path is using only /
    path = path.replace("\\", "/")
    try:
        os.remove(path)
        # Signal removal as successful
        return 0
    except OSError as err:
        print(err)
        # Return error code
        return err.args[0]


def copy_file(src, dest):
    """
    Copy a file from source to destination.

    :param src: The source path of the file.
    :type src: str

    :param dest: The destination path for the copied file.
    :type dest: str

    :return: 0 if successful, error code otherwise.
    :rtype: int
    """
    # Ensure the paths are using only /
    src = src.replace("\\", "/")
    dest = dest.replace("\\", "/")
    try:
        shutil.copy(src, dest)
        # Signal copy as successful
        return 0
    except OSError as err:
        print(err)
        # Return error code
        return err.args[0]


def execute_program(path):
    """
    Execute a program at the specified path.

    :param path: The path of the program to be executed.
    :type path: str

    :return: 0 if successful, error code otherwise.
    :rtype: int
    """
    # Ensure the path is using only /
    path = path.replace("\\", "/")
    try:
        subprocess.call(path)
        return 0
    except OSError as err:
        print(err)
        return err.args[0]
    except subprocess.CalledProcessError as err:
        print(err)
        return err.args[0]


def screenshot():
    """
    Capture a screenshot of all screens and save it as 'screenshot.jpg'.

    :return: 0 if successful, error code otherwise.
    :rtype: int
    """
    try:
        image = ImageGrab.grab(all_screens=True)
        image.save('screenshot.jpg')
        return 0
    except OSError as err:
        print(err)
        # Return error code
        return err.args[0]


def send(comm, data, data_type):
    """
    Send data over a communication channel.

    :param comm: The communication channel.
    :type comm: socket.socket

    :param data: The data to be sent.
    :type data: bytes

    :param data_type: The type of data being sent.
    :type data_type: str

    :return: 0 if successful, error code otherwise.
    :rtype: int
    """
    data_len = len(data)
    # Include type information along with the data length and actual data
    data = f"{data_type}${data_len}${data.decode()}"
    sent = 0
    try:
        while sent < len(data):
            sent += comm.send(data[sent:].encode())
        return 0
    except socket.error as err:
        print(err)
        # Return error code
        return err.args[0]


def receive(comm):
    """
    Receive data over a communication channel.

    :param comm: The communication channel.
    :type comm: socket.socket

    :return: Tuple of (data_type, received data) if successful, None otherwise.
    :rtype: tuple or None
    """
    try:
        # Receive the type and length of the data
        data_type = ""
        while True:
            char = comm.recv(1).decode()
            if char == '$':
                break
            data_type += char

        data_len_str = ""
        while True:
            char = comm.recv(1).decode()
            if char == '$':
                break
            data_len_str += char

        # Convert the length to an integer
        data_len = int(data_len_str)

        # Receive the actual data
        received_data = b""
        while len(received_data) < data_len:
            received_data += comm.recv(data_len - len(received_data))

        return data_type, received_data
    except socket.error as err:
        print(err)
        # Return None for failure
        return None
