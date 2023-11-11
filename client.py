"""
Author: Yonathan Chapal
Program name: Exc 2.7
Description: A basic commands server
Date: 10/11/2023
"""
import socket
import logging
import os

# define network constants
SERVER_IP = '127.0.0.1'
SERVER_PORT = 17207
Q_LEN = 1
MAX_PACKET = 1024
COMMAND_LEN = 4
HEADER_LEN = 2
STOP_SERVER_CONNECTION = "EXIT"
ERR_INPUT = "ERROR! unknown command!"
COMMANDS = ["DIR", "DELETE", "COPY", "EXECUTE", "TAKE SCREENSHOT", "EXIT"]

# define log constants
LOG_FORMAT = '%(levelname)s | %(asctime)s | %(processName)s | %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + '/loggerClient.log'


def send(comm, data, spaces):
    """
    Send data over a communication channel.

    :param comm: The communication channel.
    :type comm: socket.socket

    :param data: The data to be sent.
    :type data: string

    :return: 0 if successful, error code otherwise.
    :rtype: int
    """
    return_code = 0
    if not spaces:
        data = data.replace(" ", "$")
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
                received_data += buff
        else:
            received_data = None

    except socket.error as err:
        print(err)
        # Return None for failure
        received_data = None

    finally:
        return received_data


def main():
    """
       the main function; responsible for running the client code
       """
    # define an ipv4 tcp socket and listen for an incoming connection
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        logging.info(f"trying to connect to server at ({SERVER_IP}, {SERVER_PORT})")
        client.connect((SERVER_IP, SERVER_PORT))
        print("connected to server")
        logging.info("client established connection with server")
        want_to_exit = False
        print(f"valid commands: {'|'.join(COMMANDS)}")
        while not want_to_exit:
            command = input("command: ").upper()
            logging.debug(f"user entered: {command}")

            if True:
                if send(client, command, True) == 0:
                    res = receive(client)
                    # if image then print image
                    if res is not None and command != "TAKE SCREENSHOT":
                        print(f"response: {res}")
                        logging.debug(f"the server responded with {res}")
                    else:
                        print("error while receiving response from server!")
                        want_to_exit = True

                else:
                    print("error! couldn't send data to server!")
                    want_to_exit = True

                if command == STOP_SERVER_CONNECTION:
                    want_to_exit = True
            else:
                print(ERR_INPUT + ' ' + '|'.join(COMMANDS))

    except socket.error as err:
        logging.error(f"error in communication with server: {err}")

    except KeyboardInterrupt:
        logging.warning("user has stopped the program using keyboard interrupt!")
        print("stopping client.py")

        # sending the EXIT command to the server
        # note: even if I didn't add this part the server would still close the socket,
        # and everything would work as expected. It's just more correct to do it this way.
        if send(client, STOP_SERVER_CONNECTION, True) != 1:
            res = receive(client)
            if res != '':
                print(res)
                logging.debug(f"the server responded with {res}")

    finally:
        client.close()
        print("client disconnected")
        logging.info("terminated client")


if __name__ == "__main__":
    # make sure we have a logging directory and configure the logging
    if not os.path.isdir(LOG_DIR):
        print("hey")
        os.makedirs(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)

    main()
