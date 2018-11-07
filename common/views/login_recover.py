#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from bokeh.layouts import row, layout, Spacer, widgetbox
from bokeh.models.widgets.inputs import TextInput, PasswordInput
from bokeh.models.widgets.buttons import Button
from bokeh.models.widgets import Div

from flask import redirect, abort, Blueprint
from flask import request
from flask import current_app as app

from pywrapbokeh import WrapBokeh

from app.css import url_page_css, index_toolbar_menu, index_menu_redirect
from app.urls import *

from common.models import User

PAGE_URL = COMMON_URL_LOGIN_RECOVER

common_login_recover = Blueprint('common_login_recover', __name__)


@common_login_recover.route(PAGE_URL, methods=['GET', 'POST'])
def login_recover():
    logger = logging.getLogger("TMI.login_recover")

    w = WrapBokeh(PAGE_URL, logger)

    w.add("tin_uname_only", TextInput(title="User Name:", placeholder="", css_classes=['tin_uname_only']))
    w.add("tin_email_only", TextInput(title="Email:", placeholder="", css_classes=['tin_email_only']))
    w.add("b_submit", Button(label="Submit", css_classes=['b_submit']))
    w.add("b_ok", Button(label="Ok", css_classes=['b_ok']))

    w.init()

    # Create a dominate document, see https://github.com/Knio/dominate
    # this line should go after any "return redirect" statements
    w.dominate_document()
    url_page_css(w.dom_doc, PAGE_URL)

    args, _redirect_page_metrics = w.process_req(request)
    if not args: return _redirect_page_metrics
    logger.info("{} : args {}".format(PAGE_URL, args))
    left_margin = int(int(args.get("windowWidth", 800)) * 0.2)

    if args.get("b_ok", False): return redirect(COMMON_URL_INDEX)

    redir, url = index_menu_redirect(args)
    if redir: return redirect(url)

    failed_credentials_match = False
    recovery_email_sent = False
    error_fields = {}
    submitted = args.get("b_submit", False)
    if submitted:
        validated, error_fields = User.validate(args)
        if validated:
            # uname, email format is valid, now lets see if it exists
            user = User.get_username(args.get("tin_uname_only"))
            if user in [None, []] or user.email != args.get("tin_email_only"):
                logger.error("Invalid username/pw ({}/{}) for login recovery".format(user.username, args.get("tin_email_only")))
                failed_credentials_match = True

            if not failed_credentials_match:
                logger.info("user validated, sending recovery email")
                temp_pw = "12345"  # FIXME: make a random password

                # TODO: send email

                User.update(original_username=user.username,
                            first=user.fname,
                            last=user.lname,
                            username=user.username,
                            password=temp_pw,
                            email=user.email)
                recovery_email_sent = True

    doc_layout = layout(sizing_mode='scale_width')
    index_toolbar_menu(w, doc_layout, args)

    doc_layout = layout(sizing_mode='scale_width')

    # show error fields... if any
    if submitted and not validated:
        for key, value in error_fields.items():
            error = User.get_form_error_handle_from_err(key, value[0])  # process first error only
            w.add_css(key, error["css"])
            w.get(key).title = error.get('msg', "!NO MSG!")

    if recovery_email_sent:
        doc_layout.children.append(row([Spacer(width=left_margin), Div(text="""<h1>An Email has been sent!</h1>""")]))
        doc_layout.children.append(row([Spacer(width=left_margin), w.get("b_ok")]))

    elif failed_credentials_match:
        doc_layout.children.append(row([Spacer(width=left_margin), Div(text="""<h1>Those credentials did not match a known user.</h1>""", height=150)]))
        doc_layout.children.append(row([Spacer(width=left_margin), w.get("b_ok")]))

    else:
        w.add_css("tin_uname_only", {'input': {'width': '90%'}})
        w.add_css("tin_email_only", {'input': {'width': '90%'}})

        wbox = widgetbox(w.get("tin_uname_only"), w.get("tin_email_only"), w.get("b_submit"))
        doc_layout.children.append(row([Spacer(width=left_margin), wbox]))

    return w.render(doc_layout)

