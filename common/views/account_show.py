#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Example using WrapBokeh

"""
from bokeh.layouts import layout
from bokeh.models.widgets import DataTable, HTMLTemplateFormatter, TableColumn
from bokeh.models import ColumnDataSource

from flask import redirect, Blueprint, session
from flask import request

import logging
logger = logging.getLogger("TMI.account_show")

from pywrapbokeh import WrapBokeh

from app.css import url_page_css, page_toolbar_menu, toolbar_menu_redirect
from app.urls import *
from app.const import GUI

from common.models import User, RolesUsers

PAGE_URL = COMMON_URL_ACCOUNT_SHOW

common_account_show = Blueprint('common_account_show', __name__)
@common_account_show.route(PAGE_URL, methods=['GET', 'POST'])
def common__account_show():

    # TODO: This needs to be a decorator
    if not session.get('user_id', False): return redirect(COMMON_URL_LOGIN)
    user = User.get_by_id(session['user_id'])
    if user is None or not RolesUsers.user_has_role(user, ["ADMIN", "ACCOUNT"]):
        # this should never happen... logout if it does...
        logger.error("Unable to find user id {} or insufficient privileges".format(session['user_id']))
        session.pop('user_id', None)
        redirect(COMMON_URL_INDEX)

    users = User.get_username(None, True)
    data = {
        "username": [],
        "lname": [],
        "fname": [],
        "email": [],
        "roles": [],
        "_row_color": [],
    }
    for u in users:
        data["username"].append(u.username)
        data["lname"].append(u.lname)
        data["fname"].append(u.fname)
        data["email"].append(u.email)
        data["roles"].append(",".join([r.name for r in u.roles]))
        data["_row_color"].append(GUI.NOTICES_NORMAL)

    template = """<div style="background:<%=_row_color%>"; color="white";><%= value %></div>"""
    formatter = HTMLTemplateFormatter(template=template)
    hidden_columns = ["_row_color"]
    widths = {
        "username": 100,
        "lname": 100,
        "fname": 100,
        "email": 200,
        "roles": 380,
    }

    source = ColumnDataSource(data)

    columns = []
    for c in source.data.keys():
        if c not in hidden_columns:
            w = widths[c]
            columns.append(TableColumn(field=c, title=c, formatter=formatter, width=w))

    data_table = DataTable(source=source, columns=columns, width=900, height=280,
                           fit_columns=False, index_position=None)

    w = WrapBokeh(PAGE_URL, logger)

    w.init()

    # Create a dominate document, see https://github.com/Knio/dominate
    # this line should go after any "return redirect" statements
    w.dominate_document()
    url_page_css(w.dom_doc, PAGE_URL)

    args, _redirect_page_metrics = w.process_req(request)
    #if not args: return _redirect_page_metrics
    logger.info("{} : args {}".format(PAGE_URL, args))

    redir, url = toolbar_menu_redirect(args)
    if redir: return redirect(url)

    doc_layout = layout(sizing_mode='scale_width')
    page_toolbar_menu(w, doc_layout, args, user)

    doc_layout.children.append(data_table)

    return w.render(doc_layout)


