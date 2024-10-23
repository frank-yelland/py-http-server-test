#!/usr/bin/env python3
"""
dealing w/ sockets and main fn.
constants:
    PORT
    IP
functions:
    main
    listener
    handler

exit values:
    0 - ok
    1 - error loading settings
    2 - not run from the expected directory
"""

import importlib.util
import socket
import threading
from time import sleep
# import pprint
import os
import sys
from hashlib import md5

import settings
import log

import http_parse as http
import fetch

CONFIG = None
LOGGER = None


def init():
    """initialises server"""
    global LOGGER
    global CONFIG

    # initialising LOGGER to stdout
    LOGGER = log.init_logger()
    log.init_logger_stdout()
    LOGGER.info("initialised logger")


    # makes sure it's in the server directory
    directory = os.getcwd()
    directory = os.path.basename(os.path.normpath(directory))
    if directory != "server":
        LOGGER.error("server is not running from the server/ directory - \
please run from the server/ directory")
        sys.exit(2)

    # load settings
    LOGGER.info("loading settings...")
    CONFIG = settings.Settings()
    errors = CONFIG.load()

    # checking if brotli is installed
    if importlib.util.find_spec("brotli") is None:
        LOGGER.warning("brotli is not installed; please install brotli with \
'pip install brotli' or using your package manager")
    else:
        CONFIG.brotli_enabled = True
    # checking if zstd is installed
    if importlib.util.find_spec("zstd") is None:
        LOGGER.warning("zstd is not installed; pleas install zstd with 'pip \
install zstd' or using your package manager")
    else:
        CONFIG.zstd_enabled = True

    # crappy way of loading settings, easiest to think about
    http.CONFIG = CONFIG
    http.LOGGER = LOGGER
    fetch.CONFIG = CONFIG
    fetch.LOGGER = LOGGER
    log.CONFIG = CONFIG

    if errors:
        LOGGER.error("errors loading settings")
        for i, error in enumerate(errors):
            LOGGER.error("[%i] %s", i, error)
        LOGGER.info("closing server")
        sys.exit(1)
    LOGGER.info("settings loaded")

    LOGGER.info("initialising log file...")

    try:
        log.init_logger_file()
    except OSError as err:
        LOGGER.error("could not open log file: %s", str(err))
        LOGGER.info("closing server")
        sys.exit(2)

    LOGGER.info("starting listener")
    listener()

    # cleanup

    LOGGER.info("server closed")


def handler(connection, client_addr, client_id):
    """serves http requests
    Arguments:
        connection: socket object: connection to client
        client_addr: tuple: information about the connection
        client_id: int: thread id / internal id for client"""
    client = {
        "connection": connection,  # socket object
        "ip": client_addr[0],      # client ip
        "id": client_id,           # thread/client id
        "port": client_addr[1],    # client port
        "request": {
            "method": "",          # http request method
            "useragent": "",       # useragent
            "headers": {},         # request headers
            "body": b"",           # request body (if present)
            "hash": ""             # md5 hash of request
        },
        "response": {
            "headers": {},         # response headers
            "body": b"",           # response body
            "type": "",            # mime type
            "status": 200          # status code
        }
    }
    LOGGER.info("new connection from %s:%d", *client_addr)
    raw_content = connection.recv(CONFIG.max_http_header_size)
    content_hash = md5(raw_content).hexdigest()
    client.update({"request": {"hash": content_hash}})
    client = http.process_request_headers(client, raw_content)
    LOGGER.info("closing connection")
    connection.close()
    LOGGER.info("connection closed")


def listener():
    """creates a new handler for each connection"""
    # id for each connection to distinguish them when multiple connections
    # are open
    connection_id = 1
    with socket.socket() as listening_socket:
        listening_socket.bind((CONFIG.ip, CONFIG.port))
        listening_socket.listen()
        # log_info(f"started listening on ip '{IP}' and port {PORT}")
        LOGGER.info("started listening on ip '%s' and port %d",
                    CONFIG.ip,
                    CONFIG.port)
        try:
            while True:
                # opening a new thread for each connection
                try:
                    # timeout to prevent the main thread locking permanently
                    # meaning ctrl+c doesn't work
                    listening_socket.settimeout(1)
                    new_connection = listening_socket.accept()
                    threading.Thread(target=handler,
                                    args=(*new_connection, connection_id),
                                    daemon=True).start()
                    connection_id += 1
                except TimeoutError:
                    pass
        except KeyboardInterrupt:
            LOGGER.warning("ctrl+c pressed")
            closed = False
            # spinning to make sure socket is closed
            LOGGER.info("closing socket...")
            while not closed:
                try:
                    listening_socket.close()
                except OSError:
                    sleep(0.1)
            LOGGER.info("socket closed")

    LOGGER.info("lisener closed")


if __name__ == "__main__":
    init()
