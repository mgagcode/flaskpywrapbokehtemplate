#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Example using WrapBokeh

"""
import os
import sys
import logging
import logging.handlers as handlers

from flask import current_app as app


def redirect_lookup_table(value):
    if not value: return None

    app.logger.info(value)
    if   '1' in value: return "/a/"
    elif '2' in value: return "/b/"
    elif '3' in value: return "/c/"
    elif '0' in value: return "/"
    else:
        app.logger.error("Unknown link request: {}".format(value))

    return None


def setup_logging(log_file_name_prefix=__file__, path=".\log", level=logging.INFO, addConsole=False):

    # FIXME: logs are coming out "twice", once with the format from flask, and again from
    #        the format from consoleHandler.  app.logger level and the console handler
    #        level seem to be linked
    app.logger.setLevel(level)

    log_file_name_prefix = os.path.basename(log_file_name_prefix)

    # Here we define our formatter
    FORMAT = "%(relativeCreated)6d %(threadName)15s %(filename)25s:%(lineno)4s - %(name)30s:%(funcName)20s() %(levelname)-5.5s : %(message)s"
    formatter = logging.Formatter(FORMAT)

    if not os.path.exists(path): os.makedirs(path)

    allLogHandler_filename = os.path.join(path, "".join([log_file_name_prefix, ".log"]))
    allLogHandler = handlers.RotatingFileHandler(allLogHandler_filename, maxBytes=1024 * 1024, backupCount=4)
    allLogHandler.setLevel(logging.INFO)
    allLogHandler.setFormatter(formatter)

    errorLogHandler_filename = os.path.join(path, "".join([log_file_name_prefix, "-error", ".log"]))
    errorLogHandler = handlers.RotatingFileHandler(errorLogHandler_filename, maxBytes=128 * 1024, backupCount=4)
    errorLogHandler.setLevel(logging.ERROR)
    errorLogHandler.setFormatter(formatter)

    consoleHandler = logging.StreamHandler(stream=sys.stdout)
    consoleHandler.setFormatter(formatter)
    consoleHandler.setLevel(level)

    app.logger.addHandler(allLogHandler)
    app.logger.addHandler(errorLogHandler)

    if addConsole:
        app.logger.addHandler(consoleHandler)  # FIXME: reinstate when above fixme is fixed

    # this did not work :(
    # https://stackoverflow.com/questions/27775026/provide-extra-information-to-flasks-app-logger

    # this looks interesting
    # https://stackoverflow.com/questions/45775367/log-messages-not-printed-by-flask-in-my-custom-flask-extension