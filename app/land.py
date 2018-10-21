#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Example using WrapBokeh

"""
from bokeh.layouts import row, layout, Spacer, widgetbox
from bokeh.models.widgets.inputs import TextInput, PasswordInput
from bokeh.models.widgets.buttons import Button, Dropdown
from bokeh.models.widgets import Div

from flask import redirect, abort, Blueprint, session
from flask import request
from flask import current_app as app

from pywrapbokeh import WrapBokeh

from common.models import User
from app.css import url_page_css, page_toolbar_menu, toolbar_menu_redirect
from app.urls import *

PAGE_URL = COMMON_URL_LAND

app_land = Blueprint('tmi_land', __name__)


@app_land.route(PAGE_URL, methods=['GET', 'POST'])
def land():

    # TODO: This needs to be a decorator
    if not session.get('user_id', False): return redirect(COMMON_URL_LOGIN)
    user = User.get_by_id(session['user_id'])

    w = WrapBokeh(PAGE_URL, app.logger)
    w.init()

    # Create a dominate document, see https://github.com/Knio/dominate
    # this line should go after any "return redirect" statements
    w.dominate_document()
    url_page_css(w.dom_doc, PAGE_URL)

    args, _redirect_page_metrics = w.process_req(request)
    if not args: return _redirect_page_metrics
    app.logger.info("{} : args {}".format(PAGE_URL, args))

    redir, url = toolbar_menu_redirect(args)
    if redir: return redirect(url)

    doc_layout = layout(sizing_mode="fixed")
    page_toolbar_menu(w, doc_layout, args, user)

    doc_layout.children.append(Div(text="""<h1>Your Stuff Goes Here...</h1>"""))

    return w.render(doc_layout)
