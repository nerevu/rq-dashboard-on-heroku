#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

""" A script to manage development tasks """
from os import path as p
from subprocess import check_call, CalledProcessError
from urllib.parse import urlsplit

import pygogo as gogo

from flask import current_app
from flask_script import Manager

import app

BASEDIR = p.dirname(__file__)
DEF_PORT = 5000

manager = Manager(app.create_app)
manager.add_option("-m", "--cfgmode", dest="config_mode", default="Development")
manager.add_option("-f", "--cfgfile", dest="config_file", type=p.abspath)
manager.main = manager.run  # Needed to do `manage <command>` from the cli

logger = gogo.Gogo(__name__, monolog=True).logger
get_logger = lambda ok: logger.info if ok else logger.error


def log_resp(r, prefix):
    msg = r.json().get("message")
    message = "{}{}".format(prefix, msg) if prefix else msg

    if message:
        get_logger(r.ok)(message)


def notify_or_log(ok, message):
    get_logger(ok)(message)


@manager.option("-h", "--host", help="The server host")
@manager.option("-p", "--port", help="The server port", default=DEF_PORT)
@manager.option("-t", "--threaded", help="Run multiple threads", action="store_true")
def serve(port, **kwargs):
    """Runs the flask development server"""
    with current_app.app_context():
        kwargs["threaded"] = kwargs.get("threaded", current_app.config["PARALLEL"])
        kwargs["debug"] = current_app.config["DEBUG"]

        if current_app.config.get("SERVER_NAME"):
            parsed = urlsplit(current_app.config["SERVER_NAME"])
            host, port = parsed.netloc, parsed.port or port
        else:
            host = current_app.config["HOST"]

        kwargs.setdefault("host", host)
        kwargs.setdefault("port", port)
        current_app.run(**kwargs)


runserver = serve


@manager.option("-w", "--where", help="Modules to check")
def prettify(where):
    """Prettify code with black"""
    def_where = ["app.py", "manage.py", "config.py"]
    extra = where.split(" ") if where else def_where

    try:
        check_call(["black"] + extra)
    except CalledProcessError as e:
        exit(e.returncode)


@manager.option("-w", "--where", help="Modules to check")
@manager.option("-s", "--strict", help="Check with pylint", action="store_true")
def lint(where, strict):
    """Check style with linters"""
    def_where = ["app.py", "manage.py", "config.py"]
    extra = where.split(" ") if where else def_where

    try:
        check_call(["flake8"] + extra)
    except CalledProcessError as e:
        exit(e.returncode)


if __name__ == "__main__":
    manager.run()
