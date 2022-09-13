"""An autonomous sentry turret."""
import os
from typing import Final, Mapping, Optional

import toml
from flask import Flask

__version__: Final = "0.1.0"


def create_app(test_config: Optional[Mapping] = None) -> Flask:
    """Create and configure the app."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_file("config.toml", load=toml.load, silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route("/hello")
    def hello() -> str:
        return "Hello, World!"

    return app
