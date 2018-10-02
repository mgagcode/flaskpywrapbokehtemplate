#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask import current_app as app

app.config["app"] = {
    "title": "DemoApp",

    "user": {
        "roles": {
            "BASE":      "Basic",
            "EDIT-ROLE": "Roles Editor",
            "ADMIN":     "Administrator",  # rights to do anything
        },

        # these users cannot be edited
        "protected": ["admin"],

        # these users will be added if not already present
        "users": [
             {"username": "admin", "password": "qwerty", "email": "me@there.com", "roles": ["ADMIN"]},
        ],

        "signup_enabled": True,
    },
}
