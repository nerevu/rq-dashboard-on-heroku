#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

""" A script to manage development tasks """
from os import path as p
from subprocess import check_call, CalledProcessError
from urllib.parse import urlsplit

import pygogo as gogo

from flask import current_app as app
from flask_script import Manager

from app import create_app
from app.api import transfer_orders

BASEDIR = p.dirname(__file__)
DEF_PORT = 5000

manager = Manager(create_app)
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
    with app.app_context():
        kwargs["threaded"] = kwargs.get("threaded", app.config["PARALLEL"])
        kwargs["debug"] = app.config["DEBUG"]

        if app.config.get("SERVER_NAME"):
            parsed = urlsplit(app.config["SERVER_NAME"])
            host, port = parsed.netloc, parsed.port or port
        else:
            host = app.config["HOST"]

        kwargs.setdefault("host", host)
        kwargs.setdefault("port", port)
        app.run(**kwargs)


runserver = serve


@manager.option("-w", "--where", help="Modules to check")
def prettify(where):
    """Prettify code with black"""
    def_where = ["app", "manage.py", "config.py"]
    extra = where.split(" ") if where else def_where

    try:
        check_call(["black"] + extra)
    except CalledProcessError as e:
        exit(e.returncode)


@manager.option("-w", "--where", help="Modules to check")
@manager.option("-s", "--strict", help="Check with pylint", action="store_true")
def lint(where, strict):
    """Check style with linters"""
    def_where = ["app", "manage.py", "config.py"]
    extra = where.split(" ") if where else def_where

    try:
        check_call(["flake8"] + extra)
    except CalledProcessError as e:
        exit(e.returncode)


@manager.option("-o", "--order-id", help="Order ID to add")
def enqueue(order_id=None):
    """Enqueue work to be done"""
    with app.app_context():
        response = transfer_orders(order_id, enqueue=True)
        logger.debug(response)


@manager.command
def work():
    """Run the rq-worker"""
    call("python -u worker.py", shell=True)


if __name__ == "__main__":
    manager.run()
