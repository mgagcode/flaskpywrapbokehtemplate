#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import logging
from flask import Flask


def setup_logging(level=logging.INFO):

    # FIXME: logs are coming out "twice", once with the format from flask, and again from
    #        the format from consoleHandler.  app.logger level and the console handler
    #        level seem to be linked
    app.logger.setLevel(level)

    # Here we define our formatter
    FORMAT = "%(relativeCreated)6d %(threadName)15s %(filename)25s:%(lineno)4s - %(name)30s:%(funcName)20s() %(levelname)-5.5s : %(message)s"
    formatter = logging.Formatter(FORMAT)

    consoleHandler = logging.StreamHandler(stream=sys.stdout)
    consoleHandler.setFormatter(formatter)
    consoleHandler.setLevel(level)

    app.logger.addHandler(consoleHandler)

    # this did not work :(
    # https://stackoverflow.com/questions/27775026/provide-extra-information-to-flasks-app-logger


app = Flask(__name__)

@app.route('/')
def hello_world():
    app.logger.info("Foo Bar")
    return 'Hello, World!'


setup_logging()

app.run(host="0.0.0.0", port=6800, debug=False)