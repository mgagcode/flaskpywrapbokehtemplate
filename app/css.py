#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import current_app as app
from flask import url_for
from dominate.tags import *
from dominate.util import raw
from urllib.parse import urlparse

from app.urls import *
from bokeh.layouts import row, Spacer
from bokeh.models.widgets.buttons import Dropdown, Button
from bokeh.models.widgets import Div


def url_page_css(dom_doc, url):
    bkgnd_url = url_for('static', filename='media/sharon-mccutcheon-576867-unsplash.jpg', _external=False)

    with dom_doc.body:

        if url in [COMMON_URL_INDEX, COMMON_URL_LOGIN, COMMON_URL_LOGIN_SIGNUP, COMMON_URL_LOGIN_RECOVER,
                   COMMON_URL_LAND, COMMON_URL_ACCOUNT, COMMON_URL_ROLES]:
            style(raw("""body {{background: #ffffff url("{}") no-repeat left top;)}}""".format(bkgnd_url)))
            style(raw("""body {background-size: cover;)}"""))
        else:
            app.logger.error("Unknown URL: {}".format(url))


def page_toolbar_menu(w, doc_layout, args, user):
    #space_center = int(int(args.get("windowWidth", 800)) * 0.5)

    url = urlparse(args.get("windowUrl", ""))

    _menu = [
        ("Main", 'Main'),
        None,  # line divider
        ("Account", 'Account'),
        ("Roles", "Roles"),
        None,  # line divider
        ("Logout", 'Logout')
    ]

    page = ""
    if url.path == COMMON_URL_LAND:
        page = 'Main'
        _menu.remove(("Main", 'Main'))
    elif url.path == COMMON_URL_ACCOUNT:
        page = 'Edit Account'
        _menu.remove(("Account", 'Account'))
    elif url.path == COMMON_URL_ROLES:
        page = 'Edit Roles'
        _menu.remove(("Roles", "Roles"))
    else:
        app.logger.warning("{} not handled".format(url.path))

    if not w.exist("toolbar_menu"):
        w.add("toolbar_menu", Dropdown(label=user.username, menu=_menu, width=150, css_classes=['toolbar_menu']))
        w.init()
    else:
        w.get("toolbar_menu").label = user.username
        w.get("toolbar_menu").menu = _menu

    title = app.config["app"]["title"]
    doc_layout.children.append(row(Div(text="""<h1>{} - {}</h1>""".format(title, page)),
                                   Spacer(width=20),
                                   w.get("toolbar_menu"), sizing_mode="fixed"))

    w.add_css("toolbarclass", {'div': {'background-color': '#5F9EA0'}})
    w.render_div(doc_layout, cls="toolbarclass")


def index_toolbar_menu(w, doc_layout, args):
    #space_center = int(int(args.get("windowWidth", 800)) * 0.5)

    if not w.exist("b_login"):
        w.add("b_login", Button(label="LOGIN", width=50, css_classes=['b_submit']))
        w.init()

    title = app.config["app"]["title"]
    doc_layout.children.append(row(Div(text="""<h1>{}</h1>""".format(title)),
                                   Spacer(width=20),
                                   w.get("b_login"), sizing_mode="fixed"))

    w.add_css("b_login", {'button': {'background-color': '#98FB98', 'min-width': '50px'}})

    w.add_css("toolbarclass", {'div': {'background-color': '#5F9EA0'}})
    w.render_div(doc_layout, cls="toolbarclass")


def index_menu_redirect(args):
    if args.get("b_login", False): return True, COMMON_URL_LOGIN

    return False, None


def toolbar_menu_redirect(args):
    toolbar_menu = args.get("toolbar_menu", "_")

    if toolbar_menu == "": return False, None

    if toolbar_menu == "Logout":
        return True, COMMON_URL_INDEX

    if toolbar_menu == "Account":
        return True, COMMON_URL_ACCOUNT

    if toolbar_menu == "Roles":
        return True, COMMON_URL_ROLES

    if toolbar_menu == "Main":
        return True, COMMON_URL_LAND

    app.logger.warning("{} not handled".format(args.get("toolbar_menu")))
    return False, None
