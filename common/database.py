#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from flask import current_app as app

engine = create_engine('sqlite:///{}'.format("db_user.sqlite"), convert_unicode=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()


def init_db():
    logger = logging.getLogger("TMI.login")

    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import common.models as models
    Base.metadata.create_all(bind=engine)

    # populate Roles if they are not present
    s = Session()
    roles = [r.name for r in s.query(models.Role).all()]
    for role, desc in app.config["app"]["user"]["roles"].items():
        if role not in roles:
            logger.info("Adding role: {}".format(role))
            r = models.Role(name=role, description=desc)
            s.add(r)
            s.commit()

    # add default users if not present
    for user in app.config["app"]["user"]["users"]:
        user_exists = s.query(models.User).filter(models.User.username == user["username"]).scalar()
        if not user_exists:
            logger.info("Adding default user: {}".format(user["username"]))
            roles = []
            for role in user["roles"]:
                roles.append(s.query(models.Role).filter(models.Role.name == role).one())
            a = models.User(username=user["username"],
                            password=user["password"],
                            email=user["email"],
                            roles=roles)
            s.add(a)
            s.commit()

    s.close()
