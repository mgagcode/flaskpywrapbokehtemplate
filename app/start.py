#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask import current_app as app
import logging


def start():
    logger = logging.getLogger("TMI.start")

    # add your blueprints here... example...
    #from app.your_view import url_your_view
    #app.register_blueprint(url_your_view)

    app.config["app"] = {
        "title": "TMITester",

        "user": {
            "roles": {
                # Framework Roles
                "ENABLED": "Enabled",
                "BASE": "Basic",
                "ACCOUNT": "Account",
                "EDIT-ROLE": "Roles Editor",
                "ADD-USER": "Add Users",
                "ADMIN": "Administrator",  # rights to do anything

                # App specific Roles

            },

            # these users cannot be edited
            "protected": ["admin"],

            # these users will be added if not already present
            "users": [
                {"username": "admin", "password": "qwerty", "email": "me@there.com", "roles": ["ADMIN", "ENABLED"]},
            ],

            "signup_enabled": True,
        },
    }

    # init any other app stuff here
    logger.info("app start done")
