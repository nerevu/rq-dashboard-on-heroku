# -*- coding: utf-8 -*-
"""
    config
    ~~~~~~

    Provides the flask config options
    ###########################################################################
    # WARNING: if running on a a staging server, you MUST set the 'STAGE' env
    # heroku config:set STAGE=true --remote staging
    #
    # WARNING (2): The heroku project must either have a postgres, memcache, or
    # redis db to be recognized as production. If it is not recognized as
    # production, Talisman will not be run.
    ###########################################################################
"""
from os import getenv, path as p
from datetime import timedelta
from collections import namedtuple

import pygogo as gogo

from pkutils import parse_module

PARENT_DIR = p.abspath(p.dirname(__file__))
DAYS_PER_MONTH = 30

app = parse_module(p.join(PARENT_DIR, "app", "__init__.py"))
user = getenv("USER", "user")
db_env_list = ["DATABASE_URL", "REDIS_URL", "MEMCACHIER_SERVERS", "REDISTOGO_URL"]

__APP_NAME__ = app.__package_name__
__PROD_SERVER__ = any(map(getenv, db_env_list))

__DEF_HOST__ = "localhost"
__DEF_REDIS_PORT__ = 6379
__DEF_REDIS_HOST__ = getenv("REDIS_PORT_6379_TCP_ADDR", __DEF_HOST__)
__DEF_REDIS_URL__ = "redis://{}:{}".format(__DEF_REDIS_HOST__, __DEF_REDIS_PORT__)

__STAG_SERVER__ = getenv("STAGE")
__END__ = "-stage" if __STAG_SERVER__ else ""
__SUB_DOMAIN__ = f"{__APP_NAME__}{__END__}"

__CLOZE_STAGES__ = {
    "people": {
        "none": "none",
        "lead": "lead",
        "potential": "future",
        "active": "current",
        "inactive": "past",
        "lost": "out",
    },
    "projects": {
        "none": "none",
        "potential": "future",
        "active": "current",
        "done": "won",
        "lost": "lost",
    },
}

__CLOZE_ACCOUNT_MAPPINGS__ = {
    "nerevu": {
        # PEOPLE
        "lead_source": "lead-source",
        "orders_link": "orders",
        "customer_segment": "custom7",
        "customer_num": "",
        # PROJECTS
        "start": "project.start",  # same as project.created
        "value": "value",
        "customer_link": "customer",
        "amount": "amount",
        "manufacturers": "manufacturers",
        "planned_start": "planned-start",
        "order_num": "order",
        "project_segment": "project4",  # order
    },
    "alegna": {
        # PEOPLE
        "lead_source": "lead-source",
        "orders_link": "orders",
        "customer_segment": "customer",
        # TODO: this field isn't referenced
        "customer_num": "customer",
        # PROJECTS
        "start": "project.start",  # same as project.created
        "value": "value",
        "customer_link": "linked-customer",
        "amount": "win-amount",
        "manufacturers": "manufacturer",
        "planned_start": "",
        "order_num": "order",
        "project_segment": "project1",  # pricecloser order (online)
    },
}

__CLOZE_ACCOUNT_ID__ = getenv("CLOZE_ACCOUNT_ID", "nerevu")

Admin = namedtuple("Admin", ["name", "email"])
get_path = lambda name: f"file://{p.join(PARENT_DIR, 'data', name)}"
logger = gogo.Gogo(__name__, monolog=True).logger


def get_seconds(seconds=0, months=0, **kwargs):
    seconds = timedelta(seconds=seconds, **kwargs).total_seconds()

    if months:
        seconds += timedelta(DAYS_PER_MONTH).total_seconds() * months

    return int(seconds)


class Config(object):
    HEROKU = False
    TESTING = False
    PARALLEL = False
    PROD_SERVER = __PROD_SERVER__

    # see http://bootswatch.com/3/ for available swatches
    FLASK_ADMIN_SWATCH = "cerulean"
    ADMIN = Admin(app.__author__, app.__email__)
    ADMINS = frozenset([ADMIN.email])
    HOST = "127.0.0.1"

    # Variables warnings
    REQUIRED_SETTINGS = ["CLOZE_API_KEY", "CLOZE_EMAIL", "OPENCART_RESTADMIN_ID"]
    REQUIRED_PROD_SETTINGS = ["RQ_DASHBOARD_USERNAME", "RQ_DASHBOARD_PASSWORD"]

    # These don't change
    ROUTE_DEBOUNCE = get_seconds(5)
    ROUTE_TIMEOUT = get_seconds(hours=3)
    SET_TIMEOUT = get_seconds(days=30)
    LRU_CACHE_SIZE = 128
    SEND_FILE_MAX_AGE_DEFAULT = ROUTE_TIMEOUT
    EMPTY_TIMEOUT = ROUTE_TIMEOUT * 10
    API_URL_PREFIX = "/v1"
    REPORT_MONTHS = 12
    DATE_FORMAT = "%Y-%m-%d"
    RQ_DASHBOARD_REDIS_URL = (
        getenv("REDIS_URL") or getenv("REDISTOGO_URL") or __DEF_REDIS_URL__
    )
    RQ_DASHBOARD_USERNAME = getenv("RQ_DASHBOARD_USERNAME")
    RQ_DASHBOARD_PASSWORD = getenv("RQ_DASHBOARD_PASSWORD")

    # Change based on mode
    DEBUG = False
    DEBUG_MEMCACHE = True
    OAUTHLIB_INSECURE_TRANSPORT = False
    ENVIRONMENT = "production"
    CACHE_DEFAULT_TIMEOUT = get_seconds(hours=24)
    CHUNK_SIZE = 256
    ROW_LIMIT = 32
    API_RESULTS_PER_PAGE = 32
    API_MAX_RESULTS_PER_PAGE = 256
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    RQ_DASHBOARD_DEBUG = False

    # Cloze variables
    CLOZE_API_KEY = getenv("CLOZE_API_KEY")
    CLOZE_EMAIL = getenv("CLOZE_EMAIL")
    CLOZE_BASE_URL = "https://api.cloze.com/v1"
    CLOZE_ACCOUNT_MAP = __CLOZE_ACCOUNT_MAPPINGS__[__CLOZE_ACCOUNT_ID__]
    CLOZE_STAGES = __CLOZE_STAGES__
    SHARE_TO_TEAMS = True

    # OpenCart/Pricecloser variables
    OPENCART_RESTADMIN_ID = getenv("OPENCART_RESTADMIN_ID")
    PRICECLOSER_BASE_URL = "http://pricecloser.com/api/rest_admin"


class Production(Config):
    # TODO: setup nginx http://docs.gunicorn.org/en/latest/deploy.html
    #       or waitress https://github.com/etianen/django-herokuapp/issues/9
    #       test with slowloris https://github.com/gkbrk/slowloris
    #       look into preboot https://devcenter.heroku.com/articles/preboot
    defaultdb = f"postgres://{user}@{__DEF_HOST__}/{__APP_NAME__.replace('-','_')}"
    SQLALCHEMY_DATABASE_URI = getenv("DATABASE_URL", defaultdb)

    # max 20 connections per dyno spread over 4 workers
    # look into a Null pool with pgbouncer
    # https://devcenter.heroku.com/articles/python-concurrency-and-database-connections
    SQLALCHEMY_POOL_SIZE = 3
    SQLALCHEMY_MAX_OVERFLOW = 2

    HOST = "0.0.0.0"


class Heroku(Production):
    HEROKU = True
    DOMAIN = "herokuapp.com"

    if __PROD_SERVER__:
        SERVER_NAME = f"{__SUB_DOMAIN__}.{DOMAIN}"


class Custom(Production):
    DOMAIN = "nerevu.com"

    if __PROD_SERVER__:
        SERVER_NAME = f"{__SUB_DOMAIN__}.{DOMAIN}"


class Development(Config):
    base = "sqlite:///{}?check_same_thread=False"
    SQLALCHEMY_DATABASE_URI = base.format(p.join(PARENT_DIR, "app.db"))
    DEBUG = True
    DEBUG_MEMCACHE = False
    CACHE_DEFAULT_TIMEOUT = get_seconds(hours=8)
    CHUNK_SIZE = 128
    ROW_LIMIT = 16
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    OAUTHLIB_INSECURE_TRANSPORT = True
    RQ_DASHBOARD_DEBUG = True


class Ngrok(Development):
    QB_REDIRECT_URI = f"https://nerevu.ngrok.io{Config.API_URL_PREFIX}/callback"


class Test(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    DEBUG = True
    DEBUG_MEMCACHE = False
    TESTING = True
    CACHE_DEFAULT_TIMEOUT = get_seconds(hours=1)
    CHUNK_SIZE = 64
    ROW_LIMIT = 8
    OAUTHLIB_INSECURE_TRANSPORT = True
    ENVIRONMENT = "staging"
