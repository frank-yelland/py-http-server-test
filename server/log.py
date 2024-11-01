#!/usr/bin/env python3
"""
stuff for logging
constants:
    CONFIG
    LOG_FORMAT_TEMPLATE
    LOGGER
functions:
    init_logger
    init_logger_stdout
    init_logger_file
classes:
    ServerLogFormatter
"""

import logging
import logging.handlers
import datetime
import os

LOG_FORMAT_TEMPLATE = "%(asctime)s [%(threadName)s] [%(levelname)s] \
%(message)s"
DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"  # ISO8601 w/o timezone
LOGGER = None
CONFIG = None


class ServerLogFormatter(logging.Formatter):
    """logging formatter"""
    crit_colour = "\x1b[38;5;207m\x1b[1m"
    error_colour = "\x1b[38;5;160m"
    warn_colour = "\x1b[38;5;220m"
    info_colour = "\x1b[38;5;27m"
    reset_colour = "\x1b[0m"

    def __init__(self):
        """initialises custom log formatter"""
        super().__init__()
        self.formats = {
            logging.DEBUG: LOG_FORMAT_TEMPLATE,
            logging.INFO: (self.info_colour +
                           LOG_FORMAT_TEMPLATE +
                           self.reset_colour),
            logging.WARNING: (self.warn_colour +
                              LOG_FORMAT_TEMPLATE +
                              self.reset_colour),
            logging.ERROR: (self.error_colour +
                            LOG_FORMAT_TEMPLATE +
                            self.reset_colour),
            logging.CRITICAL: (self.crit_colour +
                               LOG_FORMAT_TEMPLATE +
                               self.reset_colour)
        }

    def formatTime(self, record, datefmt=None):
        """formatter for time in logs"""
        return (datetime
                .datetime
                .fromtimestamp(record.created)
                .astimezone()
                .isoformat(timespec='milliseconds'))

    def format(self, record):
        """formatter for logs"""
        log_fmt = self.formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def init_logger():
    """initialises logger, returns reference to logger"""
    global LOGGER
    # bullshit to keep within the line limit
    logging.Formatter.formatTime = (lambda self,
                                    record,
                                    datefmt=None: datetime
                                    .datetime
                                    .fromtimestamp(record.created,
                                                   datetime.timezone.utc)
                                    .astimezone()
                                    .isoformat(sep="T",
                                               timespec="milliseconds"))

    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(logging.DEBUG)
    return LOGGER


def init_logger_stdout():
    """initialises the logger on stdout"""
    stdout_log = logging.StreamHandler()
    stdout_log.setLevel(logging.DEBUG)
    stdout_log.setFormatter(ServerLogFormatter())

    LOGGER.addHandler(stdout_log)


def init_logger_file():
    """initialises the logger on the logfile"""
    # ig this should have config, name format is
    # "server_<iso time truncated to the second>.log"
    log_file_name = f"server_{datetime
                              .datetime.now()
                              .replace(microsecond=0)
                              .isoformat()}.log".replace(":", "-")

    log_dir = getattr(CONFIG, 'log_dir', None)
    if log_dir is None:
        raise FileNotFoundError("log directory location was not set")
    log_path = os.path.join(log_dir, log_file_name)
    # allegedly this is what you're supposed to do
    if os.name == "posix":
        file_log = logging.handlers.WatchedFileHandler(log_path,
                                                       encoding='utf-8')
    else:
        file_log = logging.FileHandler(log_path, encoding='utf-8')

    file_log.setLevel(logging.DEBUG)
    file_log.setFormatter(logging.Formatter(LOG_FORMAT_TEMPLATE))

    LOGGER.addHandler(file_log)
    LOGGER.info("log file initialised")
