#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask
import common.database

app = Flask(__name__)
app.secret_key = "qwerty"


@app.before_first_request
def _init_db():
    common.database.init_db()


with app.app_context():
    from common.util_logging import setup_logging
    setup_logging(log_file_name_prefix=__file__)

    # pages
    from common.views.index import common_index
    from common.views.login import common_login
    from common.views.login_signup import common_login_signup
    from common.views.login_recover import common_login_recover
    from common.views.account import common_account_edit
    from common.views.roles import common_roles_edit

    app.register_blueprint(common_index)
    app.register_blueprint(common_login)
    app.register_blueprint(common_login_signup)
    app.register_blueprint(common_account_edit)
    app.register_blueprint(common_roles_edit)
    app.register_blueprint(common_login_recover)

    from app.land import app_land
    app.register_blueprint(app_land)

    from app.app_hooks import start
    start()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6800, debug=False)


# TODO: keyboard interrupt and safe shutdown


