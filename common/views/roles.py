#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from bokeh.layouts import row, layout, Spacer, widgetbox
from bokeh.models.widgets.inputs import Select
from bokeh.models.widgets.buttons import Button
from bokeh.models.widgets import CheckboxGroup

from flask import redirect, Blueprint, session
from flask import request
from flask import current_app as app

from pywrapbokeh import WrapBokeh

from app.css import url_page_css, page_toolbar_menu, toolbar_menu_redirect
from app.urls import *

from common.models import User, Role, RolesUsers
from app.const import GUI

PAGE_URL = COMMON_URL_ROLES

common_roles_edit = Blueprint('common_roles_edit', __name__)


@common_roles_edit.route(PAGE_URL, methods=['GET', 'POST'])
def roles_edit():
    logger = logging.getLogger("TMI.roles_edit")

    def pop_session():
        session.pop("roles_initial", None)
        session.pop("roles", None)

    # TODO: This needs to be a decorator
    if not session.get('user_id', False): return redirect(COMMON_URL_LOGIN)
    user = User.get_by_id(session['user_id'])
    if user is None or not RolesUsers.user_has_role(user, ["EDIT-ROLE", "ADD-USER"]):
        # this should never happen... logout if it does...
        logger.error("Unable to find user id {}".format(session['user_id']))
        session.pop('user_id', None)
        redirect(COMMON_URL_INDEX)

    w = WrapBokeh(PAGE_URL, logger)

    w.add("sel_uname", Select(options=[], value=None, title="Select User", css_classes=['sel_uname']))
    w.add("cbg_roles", CheckboxGroup(labels=[], active=[], css_classes=['cbg_roles']))
    w.add("b_submit", Button(label="Update", css_classes=['b_submit']))
    w.add("b_cancel", Button(label="Cancel", css_classes=['b_cancel']))

    w.init()

    user = User.get_by_id(session['user_id'])
    if user is None:
        logger.error("Unable to find user id {}".format(session['user_id']))
        session.pop('user_id')
        redirect(COMMON_URL_INDEX)

    # Create a dominate document, see https://github.com/Knio/dominate
    # this line should go after any "return redirect" statements
    w.dominate_document()
    url_page_css(w.dom_doc, PAGE_URL)

    args, _redirect_page_metrics = w.process_req(request)
    if not args: return _redirect_page_metrics
    logger.info("{} : args {}".format(PAGE_URL, args))

    redir, url = toolbar_menu_redirect(args)
    if redir:
        pop_session()
        return redirect(url)

    if args.get("b_cancel", False):
        pop_session()
        return redirect(COMMON_URL_LAND)

    updated = False
    if args.get("b_submit", False) and session["roles_initial"] != w.get("cbg_roles").active:
        # need to convert the CheckboxGroup list indexes to Role IDs
        selected_idexes = w.get("cbg_roles").active
        if selected_idexes == [None]: selected_idexes = []
        selected_roles = []
        for idx in selected_idexes:
            selected_roles.append(session["roles"][idx])

        edit_user = User.get_username(w.get("sel_uname").value)
        logger.info("{} updated roles {}".format(edit_user.username, selected_roles))
        success = User.update_roles(edit_user.username, selected_roles)
        if success: updated = True

    doc_layout = layout(sizing_mode="fixed")
    page_toolbar_menu(w, doc_layout, args, user)

    # populate users
    all_users = User.get_username(None, all=True)
    sel_users = [("Select", "Select User")]
    for u in all_users:
        if u.username in app.config["app"]["user"]["protected"]: continue
        sel_users.append((u.username, u.username))
    w.get("sel_uname").options = sel_users
    w.get("sel_uname").value = args.get("sel_uname", None)  # last value or none
    session["roles_initial"] = []

    # new selection was done, update the roles
    if w.get("sel_uname").value not in ['Select', None]:
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

        if args['callerWidget'] == 'sel_uname' or updated:
            session["roles_initial"] = w.get("cbg_roles").active

    if args["callerWidget"] == 'cbg_roles':
        if len(args['cbg_roles']) == 0: w.get("cbg_roles").active = []
        else: w.get("cbg_roles").active = [int(i) for i in args['cbg_roles'].split(",")]

    # change submit button if there is a change in roles
    if session["roles_initial"] == w.get("cbg_roles").active:
        w.add_css("b_submit", {'button': {'background-color': GUI.BUTTON_DISABLED_GRAY, 'pointer-events': None}})
    else:
        w.add_css("b_submit", {'button': {'background-color': GUI.BUTTON_ENABLED_GREEN}})

    w.add_css("b_cancel", {'button': {'background-color': GUI.BUTTON_CANCEL}})

    wbox = widgetbox(w.get("sel_uname"),
                     w.get("cbg_roles"),
                     w.get("b_submit"),
                     w.get("b_cancel"))
    left_margin = int(int(args.get("windowWidth", 800)) * 0.2)
    doc_layout.children.append(row([Spacer(width=left_margin), wbox]))

    return w.render(doc_layout)

