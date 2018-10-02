#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Example using WrapBokeh

"""
from bokeh.layouts import row, layout, Spacer, widgetbox
from bokeh.models.widgets.inputs import TextInput, PasswordInput
from bokeh.models.widgets.buttons import Button
from bokeh.models.widgets import Div

from flask import redirect, abort, Blueprint, session
from flask import request
from flask import current_app as app

from pywrapbokeh import WrapBokeh

from app.css import url_page_css, page_toolbar_menu, toolbar_menu_redirect
from app.urls import *

from common.models import User

PAGE_URL = COMMON_URL_ACCOUNT

common_account_edit = Blueprint('common_account_edit', __name__)


@common_account_edit.route(PAGE_URL, methods=['GET', 'POST'])
def account_edit():

    # TODO: This needs to be a decorator
    if not session.get('user_id', False): return redirect(COMMON_URL_LOGIN)

    user = User.get_by_id(session['user_id'])
    if user is None:
        app.logger.error("Unable to find user id {}".format(session['user_id']))
        session.pop('user_id')
        w.get("tin_uname").placeholder = ""
        redirect(COMMON_URL_INDEX)

    # NOTE: !! This needs to be before the page renders
    #       !! so that the default values are populated
    if w.get("tin_uname").placeholder == "":  # trigger reset the form
        # populate initial values
        w.get("tin_fname").placeholder = user.fname
        w.get("tin_lname").placeholder = user.lname
        w.get("tin_uname").placeholder = user.username
        w.get("tin_email").placeholder = user.email
        session["original_username"] = user.username

    # Create a dominate document, see https://github.com/Knio/dominate
    # this line should go after any "return redirect" statements
    w.dominate_document()
    url_page_css(w.dom_doc, PAGE_URL)

    args, _redirect_page_metrics = w.process_req(request)
    if not args: return _redirect_page_metrics
    app.logger.info("{} : args {}".format(PAGE_URL, args))

    redir, url = toolbar_menu_redirect(args)
    if redir:
        w.get("tin_uname").placeholder = ""
        return redirect(url)

    if args.get("b_cancel", False):
        w.get("tin_uname").placeholder = ""
        return redirect(COMMON_URL_LAND)

    error_fields = {}
    submitted = args.get("b_submit", False)
    if submitted:
        validated, error_fields = User.validate(args, True)

    # on submit, validate form contents, show errors...
    if submitted and validated:
        app.logger.info("validated: {}".format(args))
        User.update(original_username=session["original_username"],
                    first=args["tin_fname"],
                    last=args["tin_lname"],
                    username=args["tin_uname"],
                    password=args["tin_lpw"],
                    email=args["tin_email"])
        session.pop('original_username')
        user = User.get_username(args["tin_uname"])
        session['user_id'] = user.id
        w.get("tin_uname").placeholder = ""  # reset the form
        return redirect(COMMON_URL_LAND)

    doc_layout = layout(sizing_mode="fixed")
    page_toolbar_menu(w, doc_layout, args, user)

    doc_layout = layout(sizing_mode='scale_width')

    # show error fields... if any
    if submitted and not validated:
        for key, value in error_fields.items():
            error = User.get_form_error_handle_from_err(key, value[0])  # process first error only
            w.add_css(key, error["css"])
            w.get(key).title = error.get('msg', "!NO MSG!")

    w.add_css("tin_fname", {'input': {'width': '90%'}})
    w.add_css("tin_lname", {'input': {'width': '90%'}})
    w.add_css("tin_uname", {'input': {'width': '90%'}})
    w.add_css("tin_lpw",   {'input': {'width': '90%'}})
    w.add_css("tin_lpw_confirm", {'input': {'width': '90%'}})
    w.add_css("tin_email", {'input': {'width': '90%'}})

    wbox = widgetbox(w.get("tin_fname"),
                     w.get("tin_lname"),
                     w.get("tin_uname"),
                     w.get("tin_lpw"),
                     w.get("tin_lpw_confirm"),
                     w.get("tin_email"),
                     w.get("b_submit"),
                     w.get("b_cancel"))
    left_margin = int(int(args.get("windowWidth", 800)) * 0.2)
    doc_layout.children.append(row([Spacer(width=left_margin), wbox]))

    return w.render(doc_layout)


w = WrapBokeh(PAGE_URL, app.logger)

w.add("tin_fname", TextInput(title="First Name:", placeholder="", css_classes=['tin_fname']))
w.add("tin_lname", TextInput(title="Last Name:", placeholder="", css_classes=['tin_lname']))
w.add("tin_uname", TextInput(title="User Name:", placeholder="", css_classes=['tin_uname']))
w.add("tin_lpw", PasswordInput(title="Password:", placeholder="", css_classes=['tin_lpw']))
w.add("tin_lpw_confirm", PasswordInput(title="Confirm Password:", placeholder="", css_classes=['tin_lpw_confirm']))
w.add("tin_email", TextInput(title="Email:", placeholder="", css_classes=['tin_email']))
w.add("b_submit", Button(label="Submit", css_classes=['b_submit']))
w.add("b_cancel", Button(label="Cancel", css_classes=['b_cancel']))

w.init()

