#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Example using WrapBokeh

"""
import os
import logging
import logging.handlers as handlers


def setup_logging(log_file_name_prefix=__file__, level=logging.INFO, path="..\log"):
    # FIXME: logs are coming out "twice", once with the format from flask, and again from
    #        the format from consoleHandler.  app.logger level and the console handler
    #        level seem to be linked

    logger = logging.getLogger("TMI")
    logger.setLevel(logging.INFO)

    log_file_name_prefix = os.path.basename(log_file_name_prefix)

    if not os.path.exists(path): os.makedirs(path)

    # Here we define our formatter
    FORMAT = "%(asctime)s %(threadName)15s %(filename)25s:%(lineno)4s - %(name)30s:%(funcName)20s() %(levelname)-5.5s : %(message)s"
    formatter = logging.Formatter(FORMAT)

    allLogHandler_filename = os.path.join(path, "".join([log_file_name_prefix, ".log"]))
    allLogHandler = handlers.RotatingFileHandler(allLogHandler_filename, maxBytes=1024 * 1024, backupCount=4)
    allLogHandler.setLevel(logging.INFO)
    allLogHandler.setFormatter(formatter)

    errorLogHandler_filename = os.path.join(path, "".join([log_file_name_prefix, "-error", ".log"]))
    errorLogHandler = handlers.RotatingFileHandler(errorLogHandler_filename, maxBytes=128 * 1024, backupCount=4)
    errorLogHandler.setLevel(logging.ERROR)
    errorLogHandler.setFormatter(formatter)

    # TODO: consider coloring logs, https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)

    logger.addHandler(allLogHandler)
    logger.addHandler(errorLogHandler)
    logger.addHandler(consoleHandler)
