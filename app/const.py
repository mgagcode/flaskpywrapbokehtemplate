#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Martin Guthrie, copyright, all rights reserved, 2018
https://stackoverflow.com/questions/2682745/how-do-i-create-a-constant-in-python
"""


class MetaConst(type):
    def __getattr__(cls, key):
        return cls[key]

    def __setattr__(cls, key, value):
        raise TypeError


class Const(object, metaclass=MetaConst):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        raise TypeError


class GUI(Const):

    INPUT_VALID = "#7FFFD4"
    INPUT_INVALID = "#FFB6C1"

    # test portal control buttons
    BUTTON_ENABLED_GREEN = "#98FB98"
    BUTTON_DISABLED_GRAY = "#A9A9A9"
    BUTTON_CANCEL = "#CD5C5C"
