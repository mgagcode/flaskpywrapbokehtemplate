#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Example using WrapBokeh

"""
from bokeh.layouts import row, layout, Spacer, widgetbox
from bokeh.models.widgets.inputs import TextInput, PasswordInput
from bokeh.models.widgets.buttons import Button

from flask import redirect, Blueprint, session
from flask import request
from flask import current_app as app

import logging
logger = logging.getLogger("TMI.account_add")

from pywrapbokeh import WrapBokeh

from app.css import url_page_css, page_toolbar_menu, toolbar_menu_redirect
from app.urls import *

from common.models import User, RolesUsers

PAGE_URL = COMMON_URL_ACCOUNT_ADD

common_account_add = Blueprint('common_account_add', __name__)
@common_account_add.route(PAGE_URL, methods=['GET', 'POST'])
def common__account_add():

    # TODO: This needs to be a decorator
    if not session.get('user_id', False): return redirect(COMMON_URL_LOGIN)
    user = User.get_by_id(session['user_id'])
    if user is None or not RolesUsers.user_has_role(user, ["ADMIN", "ADD-USER"]):
        # this should never happen... logout if it does...
        logger.error("Unable to find user id {}".format(session['user_id']))
        session.pop('user_id', None)
        redirect(COMMON_URL_INDEX)

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

    redir, url = toolbar_menu_redirect(args)
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
        return redirect(COMMON_URL_ACCOUNT_ADD)

    doc_layout = layout(sizing_mode='scale_width')
    page_toolbar_menu(w, doc_layout, args, user)


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


