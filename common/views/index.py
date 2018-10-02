#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Example using WrapBokeh

"""
from bokeh.layouts import row, layout, Spacer, widgetbox
from bokeh.models.widgets.buttons import Button
from bokeh.models.widgets import Div

from flask import redirect, abort, Blueprint, session
from flask import request
from flask import current_app as app

from pywrapbokeh import WrapBokeh

from app.css import url_page_css, index_toolbar_menu, index_menu_redirect
from app.urls import *

from common.models import q_users_last_active

PAGE_URL = COMMON_URL_INDEX

common_index = Blueprint('common_index', __name__)


@common_index.route(PAGE_URL, methods=['GET', 'POST'])
def index():
    # Create a dominate document, see https://github.com/Knio/dominate
    # this line should go after any "return redirect" statements
    w.dominate_document()
    url_page_css(w.dom_doc, PAGE_URL)

    args, _redirect_page_metrics = w.process_req(request)
    if not args: return _redirect_page_metrics
    app.logger.info("{} : args {}".format(PAGE_URL, args))

    # try and remove any sense of user when here
    try: session.pop('user_id')
    except: pass

    redir, url = index_menu_redirect(args)
    if redir: return redirect(url)

    if args.get("b_login", False): return redirect(COMMON_URL_LOGIN)

    doc_layout = layout(sizing_mode='scale_width')
    index_toolbar_menu(w, doc_layout, args)

    doc_layout = layout(sizing_mode='scale_width')

    doc_layout.children.append(Div(text="""<h1>Index Page Welcome here...</h1>"""))

    # TODO: remove this... its just debug code
    users = q_users_last_active()
    for user in users:
        print(f'{user.username}')

    print("""Session user_id: {}""".format(session.get('user_id', "None")))

    return w.render(doc_layout)


w = WrapBokeh(PAGE_URL, app.logger)
w.add("b_login", Button(label="LOGIN", width=50, css_classes=['b_submit']))
w.init()

