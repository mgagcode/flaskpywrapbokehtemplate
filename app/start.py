#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask import current_app as app

def start():

    # add your blueprints here...

    # init any other app stuff here
    app.logger.info("app start done")
