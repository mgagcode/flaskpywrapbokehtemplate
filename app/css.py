#!/usr/bin/python
# -*- coding: utf-8 -*-
import copy
from flask import current_app as app
from flask import url_for, session
from dominate.tags import *
from dominate.util import raw
from urllib.parse import urlparse

from bokeh.layouts import row, Spacer
from bokeh.models.widgets.buttons import Dropdown, Button
from bokeh.models.widgets import Div

from app.urls import *
from app.const import GUI
from app.app_hooks import logout
from common.models import RolesUsers


def url_page_css(dom_doc, url):
    """ Add css to the page
    :param dom_doc:
    :param url: url of the current page
    """
    bkgnd_url = url_for('static', filename='media/sharon-mccutcheon-576867-unsplash.jpg', _external=False)

    # based on url, you can specify different css for that page...
    # if (usrl == <>):

    with dom_doc.body:
        style(raw("""body {{background: #ffffff url("{}") no-repeat left top;)}}""".format(bkgnd_url)))
        style(raw("""body {background-size: cover;)}"""))


# menu base here has all the common items, app:start.py needs to add other menu items
_page_toolbar_menu = [
    {"entry": ("Main", 'Main'), "url": COMMON_URL_LAND, "title": "Main"},
    {"entry": None, "url": None, "title": None},  # line divider
    {"entry": ("Account", 'Account'), "url": COMMON_URL_ACCOUNT, "title": "Edit Account", "role": ["ACCOUNT"]},
    {"entry": ("Roles", "Roles"), "url": COMMON_URL_ROLES, "title": "Edit Roles", "role": ["EDIT-ROLE", "ADD-USER"]},
    {"entry": ("Add Users", "Add Users"), "url": COMMON_URL_ACCOUNT_ADD, "title": "Add Users", "role": ["ADD-USER"]},
    {"entry": ("Show Users", "Show Users"), "url": COMMON_URL_ACCOUNT_SHOW, "title": "Show Users", "role": ["ACCOUNT"]},
    {"entry": None, "url": None, "title": None},  # line divider
    {"entry": ("Logout", 'Logout'), "url": COMMON_URL_INDEX, "title": "Logout"},
]


def page_toolbar_menu_add(idx, entry, url, title, role=[]):
    menu = {"entry": (entry, entry), "url": url, "title": title, "role": role}
    _page_toolbar_menu.insert(idx, menu)


def page_toolbar_menu(w, doc_layout, args, user, buttons=[]):
    url = urlparse(args.get("windowUrl", ""))

    _new_menu = copy.deepcopy(_page_toolbar_menu)
    sub_title = ""

    # remove menu item for the page that we are already on or user doesn't have priviliage
    for entry in _page_toolbar_menu:
        if url.path == entry["url"]:
            _new_menu.remove(entry)
            sub_title = entry["title"]  # this is the page we are on, add to toolbar row display

        if entry.get("role", False) and not RolesUsers.user_has_role(user, entry["role"]):
            _new_menu.remove(entry)

    _new_menu = [x["entry"] for x in _new_menu]

    w.add("toolbar_menu", Dropdown(label=user.username, menu=_new_menu, width=GUI.TITLEBAR_MENU_WIDTH, css_classes=['toolbar_menu']))
    w.init()

    title = app.config["app"]["title"]
    _tool_bar_row = [Div(text="""<h1>{} - {}</h1>""".format(title, sub_title), width=GUI.TITLEBAR_TITLE_WIDTH)]
    _tool_bar_row.append(w.get("toolbar_menu"))
    for button in buttons:
        _tool_bar_row.append(Spacer(width=GUI.TITLEBAR_SPACER))
        _tool_bar_row.append(button)
    doc_layout.children.append(row(_tool_bar_row))

    w.add_css("toolbarclass", {'div': {'background-color': '#5F9EA0'}})


def index_toolbar_menu(w, doc_layout, args):
    w.add("b_login", Button(label="LOGIN", width=GUI.TITLEBAR_LOGIN_BTN_WIDTH, css_classes=['b_submit']))

    title = app.config["app"]["title"]
    doc_layout.children.append(row(Div(text="""<h1>{}</h1>""".format(title), width=GUI.TITLEBAR_TITLE_WIDTH),
                                   Spacer(width=GUI.TITLEBAR_SPACER),
                                   w.get("b_login"), sizing_mode="fixed"))

    w.add_css("b_login", {'button': {'background-color': '#98FB98', 'min-width': '50px'}})
    w.add_css("toolbarclass", {'div': {'background-color': '#5F9EA0'}})


def index_menu_redirect(args):

    # for debugging... log in directly
    if 0:
        session['user_id'] = 2
        return True, COMMON_URL_LAND

    if args.get("b_login", False): return True, COMMON_URL_LOGIN

    return False, None


def toolbar_menu_redirect(args):
    if args.get("callerWidget", "") != "toolbar_menu": return False, None
    toolbar_menu = args.get("toolbar_menu", "")
    if toolbar_menu in ["", 'null']: return False, None

    for entry in _page_toolbar_menu:
        if entry["entry"] is None: continue
        if toolbar_menu == entry["entry"][0]:
            app.logger.info("toolbar {} -> {}".format(toolbar_menu, entry["url"]))
            if COMMON_URL_INDEX == entry["url"]: logout()
            return True, entry["url"]

    app.logger.warning("{} not handled".format(args.get("toolbar_menu")))
    return False, None
