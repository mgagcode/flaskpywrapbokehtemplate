#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Example using WrapBokeh

"""
import logging
logger = logging.getLogger("TMI.login")

from bokeh.layouts import row, layout, Spacer, widgetbox, column
from bokeh.models.widgets.inputs import TextInput, PasswordInput
from bokeh.models.widgets.buttons import Button
from bokeh.models.widgets import Div

from flask import redirect, abort, Blueprint, session
from flask import request
from flask import current_app as app

from pywrapbokeh import WrapBokeh

from app.css import url_page_css, index_toolbar_menu, index_menu_redirect
from app.urls import *

from common.models import User

PAGE_URL = COMMON_URL_LOGIN

common_login = Blueprint('common_login', __name__)
@common_login.route(PAGE_URL, methods=['GET', 'POST'])
def login():

    w = WrapBokeh(PAGE_URL, logger)

    w.add("tin_uname", TextInput(title="Login Name:", placeholder="", css_classes=['tin_lname']))
    w.add("tin_lpw", PasswordInput(title="Password:", placeholder="", css_classes=['tin_lpw']))
    w.add("b_submit", Button(label="Submit", css_classes=['b_submit']))
    w.add("b_signup", Button(label="Sign Up", css_classes=['b_signup']))
    w.add("b_recover", Button(label="Recover Password", css_classes=['b_recover']))

    w.init()

    # Create a dominate document, see https://github.com/Knio/dominate
    # this line should go after any "return redirect" statements
    w.dominate_document()
    url_page_css(w.dom_doc, PAGE_URL)

    args, _redirect_page_metrics = w.process_req(request)
    if not args: return _redirect_page_metrics
    logger.info("{} : args {}".format(PAGE_URL, args))
    left_margin = int(int(args.get("windowWidth", 800)) * 0.1)

    redir, url = index_menu_redirect(args)
    if redir: return redirect(url)

    if args.get("b_signup", False): return redirect(COMMON_URL_LOGIN_SIGNUP)
    if args.get("b_recover", False): return redirect(COMMON_URL_LOGIN_RECOVER)

    login_failed = False
    if args.get("b_submit", False):
        uname = args.get("tin_uname", None)
        pw = args.get("tin_lpw", None)

        if uname is not None and pw is not None:
            user = User.login(uname, pw)
            if user is not None:
                logger.info("{} {}".format(user.username, user.id))
                session['user_id'] = user.id
                return redirect(COMMON_URL_LAND)
            else:
                logger.info("Login failed for {}".format(uname))
                login_failed = True

    doc_layout = layout(sizing_mode='scale_width')
    index_toolbar_menu(w, doc_layout, args)

    doc_layout = layout(sizing_mode='scale_width')

    if login_failed:
        doc_layout.children.append(row(Spacer(width=left_margin), column([Div(text="""<p>Login failed, Recover Password?</p>"""),
                                                                          w.get("b_recover")])))

    w.add_css("b_submit",  {'button': {'background-color': '#98FB98', 'min-width': '60px'}})
    w.add_css("b_signup",  {'button': {'background-color': '#98FB98', 'min-width': '60px'}})
    w.add_css("tin_uname", {'input':  {'width': '90%'}})
    w.add_css("tin_lpw",   {'input':  {'width': '90%'}})

    if app.config["app"]["user"]["signup_enabled"]:
        wbox = widgetbox(w.get("tin_uname"), w.get("tin_lpw"), w.get("b_submit"), w.get("b_signup"))
    else:
        wbox = widgetbox(w.get("tin_uname"), w.get("tin_lpw"), w.get("b_submit"))

    doc_layout.children.append(row([Spacer(width=left_margin), wbox]))

    return w.render(doc_layout)
