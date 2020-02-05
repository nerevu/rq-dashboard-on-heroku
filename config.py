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

app = parse_module(p.join(PARENT_DIR, "app.py"))
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
    ADMIN = Admin(app.__author__, app.__email__)
    ADMINS = frozenset([ADMIN.email])
    HOST = "127.0.0.1"

    # Variables warnings
    REQUIRED_PROD_SETTINGS = ["RQ_DASHBOARD_USERNAME", "RQ_DASHBOARD_PASSWORD"]

    # These don't change
    ROUTE_DEBOUNCE = get_seconds(5)
    ROUTE_TIMEOUT = get_seconds(hours=3)
    SET_TIMEOUT = get_seconds(days=30)
    LRU_CACHE_SIZE = 128
    SEND_FILE_MAX_AGE_DEFAULT = ROUTE_TIMEOUT
    EMPTY_TIMEOUT = ROUTE_TIMEOUT * 10
    API_URL_PREFIX = "/v1"
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
    RQ_DASHBOARD_DEBUG = False


class Production(Config):
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
    DEBUG = True
    DEBUG_MEMCACHE = False
    CACHE_DEFAULT_TIMEOUT = get_seconds(hours=8)
    CHUNK_SIZE = 128
    ROW_LIMIT = 16
    OAUTHLIB_INSECURE_TRANSPORT = True
    RQ_DASHBOARD_DEBUG = True


class Test(Config):
    DEBUG = True
    DEBUG_MEMCACHE = False
    TESTING = True
    CACHE_DEFAULT_TIMEOUT = get_seconds(hours=1)
    CHUNK_SIZE = 64
    ROW_LIMIT = 8
    OAUTHLIB_INSECURE_TRANSPORT = True
    ENVIRONMENT = "staging"
