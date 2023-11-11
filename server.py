"""
Author: Yonathan Chapal
Program name: Exc 2.7
Description: A basic commands server
Date: 10/11/2023
"""

import socket
import logging
import glob
import os
import shutil
import subprocess
from PIL import ImageGrab

# define network constants
LISTEN_IP = '0.0.0.0'
LISTEN_PORT = 17207
Q_LEN = 1
MAX_PACKET = 1024
EXCEPTED_REQUEST_TYPE = 'str'

# define log constants
LOG_FORMAT = '%(levelname)s | %(asctime)s | %(processName)s | %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + '/loggerServer.log'


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

    return str(files)


def delete_file(path):
    """
    Delete a file at the specified path.

    :param path: The path of the file to be deleted.
    :type path: str

    :return: 0 if successful, error code otherwise.
    :rtype: int
    """
    return_code = 0
    # Ensure the path is using only /
    path = path.replace("\\", "/")
    try:
        os.remove(path)
        # Signal removal as successful
    except OSError as err:
        print(err)
        # Return error code
        return_code = err.args[0]

    return return_code


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
    return_code = 0
    # Ensure the paths are using only /
    src = src.replace("\\", "/")
    dest = dest.replace("\\", "/")
    try:
        shutil.copy(src, dest)
        # Signal copy as successful
    except OSError as err:
        print(err)
        # Return error code
        return_code = err.args[0]

    return return_code


def execute_program(path):
    """
    Execute a program at the specified path.

    :param path: The path of the program to be executed.
    :type path: str

    :return: 0 if successful, error code otherwise.
    :rtype: int
    """
    return_code = 0
    # Ensure the path is using only /
    path = path.replace("\\", "/")
    try:
        subprocess.call(path)
    except OSError as err:
        print(err)
        return_code = err.args[0]
    except subprocess.CalledProcessError as err:
        print(err)
        return_code = err.args[0]

    return return_code


def screenshot():
    """
    Capture a screenshot of all screens and save it as 'screenshot.jpg'.

    :return: 0 if successful, error code otherwise.
    :rtype: int
    """
    return_value = None
    try:
        ImageGrab.grab(all_screens=True).save('screenshot.jpg')
        # call function to read photo
    except OSError as err:
        print(err)
        # Return error code
        return_value = None

    return return_value


def send(comm, data):
    """
    Send data over a communication channel.

    :param comm: The communication channel.
    :type comm: socket.socket

    :param data: The data to be sent.
    :type data: str

    :return: 0 if successful, error code otherwise.
    :rtype: int
    """
    return_code = 0
    data_len = len(data)
    # Include type information along with the data length and actual data
    data = str(data_len) + '$' + data
    sent = 0
    try:
        while sent < len(data):
            sent += comm.send(data[sent:].encode())

    except socket.error as err:
        print(err)
        # Return error code
        return_code = err.args[0]

    return return_code


def receive(comm):
    """
    Receive data over a communication channel.

    :param comm: The communication channel.
    :type comm: socket.socket

    :return: string of the data from the client if successful, None otherwise.
    :rtype: str or None
    """
    data_len_str = ""
    received_data = ""
    try:
        # Receive length of the data
        while True:
            buff = comm.recv(1).decode()
            if buff == '$':
                break
            if buff == '':
                data_len_str = None
                break
            data_len_str += buff

        # Convert the length to an integer
        if data_len_str is not None:
            data_len = int(data_len_str)

            # Receive the actual data
            i = 0
            while len(received_data) < data_len:
                buff = comm.recv(data_len - len(received_data)).decode()
                if buff == '':
                    received_data = None
                    break
                received_data[i] += buff
            received_data = received_data.split("$")
        else:
            received_data = None

    except socket.error as err:
        print(err)
        # Return None for failure
        received_data = None

    finally:
        return received_data


# def assert user response

def handle_general(comm, message, num_of_args, return_data, func):
    return_code = 0
    try:
        if num_of_args != 0 and message is not None:
            return_code = send(comm, message)
            if return_code == 0:
                res = receive(comm)
                if res is not None:
                    data = func(*res[:num_of_args])
                    if return_data:  # signify if you want to return the function return value
                        return_code = send(comm, data)
                    else:
                        return_code = data

        elif num_of_args == 0 and message is None:
            data = func()
            if return_data:
                return_code = send(comm, data)
            else:
                return_code = data
        else:
            # this function operates on the assumption that,
            # if you need arguments for function, you need to send client a message and vice versa.
            return_code = 1
    except socket.error as err:
        print(err)
        return_code = err.args[0]
    return return_code


def main():
    """
    the main function; responsible for running the server code
    """
    # define an ipv4 tcp socket and listen for an incoming connection
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        serv.bind((LISTEN_IP, LISTEN_PORT))
        serv.listen(Q_LEN)
        logging.debug(f"server is listening on port {LISTEN_PORT}")
        while True:
            # accept connection
            logging.info("waiting for connection...")
            conn, addr = serv.accept()
            logging.info("connection established")
            disconnect = False
            try:
                while not disconnect:
                    req = receive(conn)
                    if req is not None:
                        req = [x.upper() for x in req]

                        if req == "DIR":
                            r_code = handle_general(conn, "ENTER PATH", 1, True, get_file_list)
                            if r_code != 0:
                                disconnect = True
                        elif req == "DELETE":
                            r_code = handle_general(conn, "ENTER PATH", 1, False, get_file_list)
                            if r_code != 0 or (r_code == 0 and send(conn, "FILE DELETED") != 0):
                                disconnect = True

                        elif req == "COPY":
                            r_code = handle_general(conn, "ENTER PATHS", 2, False, get_file_list)
                            if r_code != 0 or (r_code == 0 and send(conn, "FILE COPIED") != 0):
                                disconnect = True
                        # handle copy request
                        elif req == "EXECUTE":
                            r_code = handle_general(conn, "ENTER PATH", 1, False, get_file_list)
                            if r_code != 0 or (r_code == 0 and send(conn, "PROGRAM EXECUTED") != 0):
                                disconnect = True
                        # handle execute request
                        elif req == "TAKE SCREENSHOT":
                            r_code = handle_general(conn, None, 0, True, get_file_list)
                            if r_code != 0:
                                disconnect = True
                        # handle screenshot request
                        elif req == "EXIT":
                            # send disconnect message
                            send(conn, "GOODBYE")
                            disconnect = True
                        else:
                            print("unknown command")
                            if send(conn, "Unknown command") != 0:
                                disconnect = True
                    else:
                        print("error in request")
                        disconnect = True
            except socket.error as err:
                logging.error(f"error in communication with client: {err}")
            finally:
                conn.close()
                logging.info("terminated connection with client socket")

    except socket.error as err:
        logging.error(f"error while opening server socket: {err}")

    finally:
        serv.close()


if __name__ == "__main__":
    # make sure we have a logging directory and configure the logging
    if not os.path.isdir(LOG_DIR):
        print("hey")
        os.makedirs(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)

    main()
