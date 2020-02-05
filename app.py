# -*- coding: utf-8 -*-
"""
    app
    ~~~

    Provides the flask application
"""

from flask import Flask, redirect, request
from datetime import date

import pygogo as gogo

from rq_dashboard import default_settings
from rq_dashboard.cli import add_basic_auth

import config

__version__ = "0.8.1"
__title__ = "nerevu-rq-dashboard"
__package_name__ = "nerevu-rq-dashboard"
__author__ = "Mitchell Sottom"
__description__ = "Adds Pricecloser orders to Cloze"
__email__ = "msotto@nerevu.com"
__license__ = "MIT"
__copyright__ = f"Copyright {date.today().year} Nerevu Group"

logger = gogo.Gogo(__name__, monolog=True).logger


def create_app(config_mode=None, config_file=None):
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    required_setting_missing = False

    @app.before_request
    def clear_trailing():
        request_path = request.path

        if request_path != "/" and request_path.endswith("/"):
            return redirect(request_path[:-1])

    app.config.from_object(default_settings)

    if config_mode:
        app.config.from_object(getattr(config, config_mode))
    elif config_file:
        app.config.from_pyfile(config_file)
    else:
        app.config.from_envvar("APP_SETTINGS", silent=True)

    username = app.config.get("RQ_DASHBOARD_USERNAME")
    password = app.config.get("RQ_DASHBOARD_PASSWORD")
    prefix = app.config.get("API_URL_PREFIX")
    server_name = app.config.get("SERVER_NAME")

    for setting in app.config.get("REQUIRED_SETTINGS", []):
        if not app.config.get(setting):
            required_setting_missing = True
            logger.error(f"App setting {setting} is missing!")

    if app.config.get("PROD_SERVER"):
        if server_name:
            logger.info(f"SERVER_NAME is {server_name}.")
        else:
            logger.error(f"SERVER_NAME is not set!")

        for setting in app.config.get("REQUIRED_PROD_SETTINGS", []):
            if not app.config.get(setting):
                required_setting_missing = True
                logger.error(f"App setting {setting} is missing!")

    if not required_setting_missing:
        logger.info(f"All required app settings present!")

    if username and password:
        add_basic_auth(blueprint=rq, username=username, password=password)
        logger.info(f"Creating RQ-dashboard login for {username}")

    app.register_blueprint(rq, url_prefix=f"{prefix}/dashboard")

    @app.route("/")
    def root():
        return redirect(f"{prefix}/dashboard", code=302)

    return app


# put at bottom to avoid circular reference errors
from rq_dashboard import blueprint as rq  # noqa
