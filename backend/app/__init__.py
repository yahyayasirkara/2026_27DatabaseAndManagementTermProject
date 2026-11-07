from flask import Flask, jsonify
from app.config import Config
from app.extensions import jwt, swagger

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Eklentileri uygulamaya bağla
    jwt.init_app(app)
    swagger.init_app(app)

    from app.controllers.oda_tipi_controller import oda_tipi_bp
    app.register_blueprint(oda_tipi_bp)

    @app.route('/')
    def index():
        return jsonify({"mesaj": "Modüler Flask Backend Başarıyla Çalışıyor!"})

    return app