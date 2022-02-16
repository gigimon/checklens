import os
import sys
import logging

import redis
from flask import Flask

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")


LOG = logging.getLogger(__name__)


def configure_redis():
    host = os.environ.get("REDIS_HOST")

    if host is None:
        LOG.error("You must setup REDIS_HOST environment variable")
        sys.exit(1)
    port = os.environ.get("REDIS_PORT", "6379")
    db = os.environ.get("REDIS_DB", "0")

    conn = redis.Redis(host=host, port=port, db=db)
    return conn


def create_app():
    app = Flask(__name__)

    check_field = os.environ.get("CHECK_FIELD_EXISTS")

    if check_field is None:
        LOG.error("Env variable CHECK_FIELD_EXISTS clean")
        sys.exit(1)

    if len(check_field.split(".")) != 3:
        LOG.error("Please use 'field1.child_a.child_b' format for CHECK_FIELD_EXISTS")
        sys.exit(1)

    app.config["validate_field"] = check_field
    app.config["redis"] = configure_redis()

    from .app import main_bp

    app.register_blueprint(main_bp)

    return app