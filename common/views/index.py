#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Example using WrapBokeh

"""
from bokeh.layouts import layout
from bokeh.models.widgets.buttons import Button
from bokeh.models.widgets import Div

from flask import redirect, Blueprint, session
from flask import request
from flask import current_app as app

from pywrapbokeh import WrapBokeh

from app.css import url_page_css, index_toolbar_menu, index_menu_redirect
from app.urls import *

PAGE_URL = COMMON_URL_INDEX

common_index = Blueprint('common_index', __name__)


@common_index.route(PAGE_URL, methods=['GET', 'POST'])
def index():
    session.clear()

    w = WrapBokeh(PAGE_URL, app.logger)

    # Create a dominate document, see https://github.com/Knio/dominate
    # this line should go after any "return redirect" statements
    w.dominate_document()
    url_page_css(w.dom_doc, PAGE_URL)

    args, _redirect_page_metrics = w.process_req(request)
    if not args: return _redirect_page_metrics
    app.logger.info("{} : args {}".format(PAGE_URL, args))

    redir, url = index_menu_redirect(args)
    if redir: return redirect(url)

    if args.get("b_login", False): return redirect(COMMON_URL_LOGIN)

    doc_layout = layout(sizing_mode='scale_width')
    index_toolbar_menu(w, doc_layout, args)

    doc_layout.children.append(Div(text="""<h1>Index Page Welcome here...</h1>"""))

    w.init()

    return w.render(doc_layout)




