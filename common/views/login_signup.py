#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Example using WrapBokeh

"""
import logging
from bokeh.layouts import row, layout, Spacer, widgetbox
from bokeh.models.widgets.inputs import TextInput, PasswordInput
from bokeh.models.widgets.buttons import Button

from flask import redirect, abort, Blueprint
from flask import request
from flask import current_app as app

from pywrapbokeh import WrapBokeh

from app.css import url_page_css, index_toolbar_menu, index_menu_redirect
from app.urls import *

from common.models import User

PAGE_URL = COMMON_URL_LOGIN_SIGNUP

common_login_signup = Blueprint('common_login_signup', __name__)


@common_login_signup.route(PAGE_URL, methods=['GET', 'POST'])
def login_signup():
    logger = logging.getLogger("TMI.login_recover")

    w = WrapBokeh(PAGE_URL, logger)

    w.add("tin_fname", TextInput(title="First Name:", placeholder="", css_classes=['tin_fname']))
    w.add("tin_lname", TextInput(title="Last Name:", placeholder="", css_classes=['tin_lname']))
    w.add("tin_uname", TextInput(title="User Name:", placeholder="", css_classes=['tin_uname']))
    w.add("tin_lpw", PasswordInput(title="Password:", placeholder="", css_classes=['tin_lpw']))
    w.add("tin_lpw_confirm", PasswordInput(title="Confirm Password:", placeholder="", css_classes=['tin_lpw_confirm']))
    w.add("tin_email", TextInput(title="Email:", placeholder="", css_classes=['tin_email']))
    w.add("b_submit", Button(label="Submit", css_classes=['b_submit']))

    w.init()

    # Create a dominate document, see https://github.com/Knio/dominate
    # this line should go after any "return redirect" statements
    w.dominate_document()
    url_page_css(w.dom_doc, PAGE_URL)

    args, _redirect_page_metrics = w.process_req(request)
    if not args: return _redirect_page_metrics
    logger.info("{} : args {}".format(PAGE_URL, args))

    redir, url = index_menu_redirect(args)
    if redir: return redirect(url)

    error_fields = {}
    submitted = args.get("b_submit", False)
    if submitted:
        validated, error_fields = User.validate(args)

    # on submit, validate form contents, show errors...
    if submitted and validated:
        logger.info("validated: {}".format(args))
        User.add(first=args["tin_fname"],
                 last=args["tin_lname"],
                 username=args["tin_uname"],
                 password=args["tin_lpw"],
                 email=args["tin_email"])
        return redirect(COMMON_URL_INDEX)

    doc_layout = layout(sizing_mode='scale_width')
    index_toolbar_menu(w, doc_layout, args)

    # show error fields... if any
    if submitted and not validated:
        for key, value in error_fields.items():
            error = User.get_form_error_handle_from_err(key, value[0])  # process first error only
            w.add_css(key, error["css"])
            w.get(key).title = error.get('msg', "!NO MSG!")

    w.add_css("tin_fname", {'input': {'width': '90%'}})
    w.add_css("tin_lname", {'input': {'width': '90%'}})
    w.add_css("tin_uname", {'input': {'width': '90%'}})
    w.add_css("tin_lpw", {'input': {'width': '90%'}})
    w.add_css("tin_lpw_confirm", {'input': {'width': '90%'}})
    w.add_css("tin_email", {'input': {'width': '90%'}})

    wbox = widgetbox(w.get("tin_fname"),
                     w.get("tin_lname"),
                     w.get("tin_uname"),
                     w.get("tin_lpw"),
                     w.get("tin_lpw_confirm"),
                     w.get("tin_email"),
                     w.get("b_submit"))
    left_margin = int(int(args.get("windowWidth", 800)) * 0.2)
    doc_layout.children.append(row([Spacer(width=left_margin), wbox]))

    return w.render(doc_layout)


