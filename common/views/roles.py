#!/usr/bin/python
# -*- coding: utf-8 -*-

from bokeh.layouts import row, layout, Spacer, widgetbox
from bokeh.models.widgets.inputs import TextInput, Select
from bokeh.models.widgets.buttons import Button
from bokeh.models.widgets import Div
from bokeh.models.widgets import CheckboxGroup

from flask import redirect, abort, Blueprint, session
from flask import request
from flask import current_app as app

from pywrapbokeh import WrapBokeh

from app.css import url_page_css, page_toolbar_menu, toolbar_menu_redirect
from app.urls import *

from common.models import User, Role, RolesUsers

PAGE_URL = COMMON_URL_ROLES

common_roles_edit = Blueprint('common_roles_edit', __name__)


@common_roles_edit.route(PAGE_URL, methods=['GET', 'POST'])
def roles_edit():

    # TODO: This needs to be a decorator
    if not session.get('user_id', False): return redirect(COMMON_URL_LOGIN)

    user = User.get_by_id(session['user_id'])
    if user is None:
        app.logger.error("Unable to find user id {}".format(session['user_id']))
        session.pop('user_id')
        redirect(COMMON_URL_INDEX)

    # Create a dominate document, see https://github.com/Knio/dominate
    # this line should go after any "return redirect" statements
    w.dominate_document()
    url_page_css(w.dom_doc, PAGE_URL)

    args, _redirect_page_metrics = w.process_req(request)
    if not args: return _redirect_page_metrics
    app.logger.info("{} : args {}".format(PAGE_URL, args))

    redir, url = toolbar_menu_redirect(args)
    if redir:
        init_widgets()
        return redirect(url)

    if args.get("b_cancel", False):
        init_widgets()
        return redirect(COMMON_URL_LAND)

    update_roles = False
    if args.get("b_submit", False) and session["roles_initial"] != w.get("cbg_roles").active:
        # need to convert the CheckboxGroup list indexes to Role IDs
        selected_idexes = w.get("cbg_roles").active
        if selected_idexes == [None]: selected_idexes = []
        selected_roles = []
        for idx in selected_idexes:
            selected_roles.append(session["roles"][idx])

        edit_user = User.get_username(w.get("sel_uname").value)
        app.logger.info("{} updated roles {}".format(edit_user.username, selected_roles))
        User.update_roles(edit_user, selected_roles)
        update_roles = True

    doc_layout = layout(sizing_mode="fixed")
    page_toolbar_menu(w, doc_layout, args, user)

    # if the user is not a role editor or admin, then bail
    if not RolesUsers.user_has_role(user, ["ADMIN", "EDIT-ROLE"]):
        app.logger.info("{} (id={}) does not have roles edit privileges".format(user.username, user.id))
        doc_layout = layout(sizing_mode='scale_width')
        doc_layout.children.append(Div(text="""<h1>You do not have access rights for this operation.</h1>"""))
        return w.render(doc_layout)

    if not w.get("sel_uname").options:  # indicates first time thru, populate select
        all_users = User.get_username(None, all=True)
        sel_users = [("None", "Select User")]
        for u in all_users:
            if u.username in app.config["app"]["user"]["protected"]: continue
            sel_users.append((u.username, u.username))
        w.get("sel_uname").options = sel_users
        w.get("sel_uname").value = None
        session["roles_initial"] = []

    if args.get("callerWidget", "") == "sel_uname" or update_roles:
        # new selection was done, update the roles
        edit_user = User.get_username(w.get("sel_uname").value)
        roles = []
        user_ids = []
        session["roles"] = []
        for _id, _name, _desc in Role.get_all():
            session["roles"].append(_name)
            roles.append(_desc)
            if RolesUsers.user_has_role(edit_user, _name):
                user_ids.append(roles.index(_desc))
        w.get("cbg_roles").labels = roles
        w.get("cbg_roles").active = user_ids
        session["roles_initial"] = w.get("cbg_roles").active

    doc_layout = layout(sizing_mode='scale_width')

    # change submit button if there is a change in roles
    if session["roles_initial"] == w.get("cbg_roles").active:
        w.add_css("b_submit", {'button': {'background-color': '#D3D3D3'}})
    else:
        w.add_css("b_submit", {'button': {'background-color': '#90EE90'}})

    wbox = widgetbox(w.get("sel_uname"),
                     w.get("cbg_roles"),
                     w.get("b_submit"),
                     w.get("b_cancel"))
    left_margin = int(int(args.get("windowWidth", 800)) * 0.2)
    doc_layout.children.append(row([Spacer(width=left_margin), wbox]))

    return w.render(doc_layout)


def init_widgets():
    w.get("sel_uname").options = []
    w.get("sel_uname").value = None
    w.get("cbg_roles").labels = []
    w.get("cbg_roles").active = []


w = WrapBokeh(PAGE_URL, app.logger)

w.add("sel_uname", Select(options=[], value=None, title="Select User", css_classes=['sel_uname']))
w.add("cbg_roles", CheckboxGroup(labels=[], active=[], css_classes=['cbg_roles']))
w.add("b_submit", Button(label="Update", css_classes=['b_submit']))
w.add("b_cancel", Button(label="Cancel", css_classes=['b_cancel']))

w.init()

