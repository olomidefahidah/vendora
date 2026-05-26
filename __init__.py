from pathlib import Path

from flask import Flask

from .routes import main
from .store import VendoraStore


def create_app():
    base_dir = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(base_dir / "templates"),
        static_folder=str(base_dir / "static"),
    )
    app.config["SECRET_KEY"] = "vendora-development-key"
    app.config["STORE"] = VendoraStore()
    app.config["STORE"].load_all()
    app.register_blueprint(main)
    return app
