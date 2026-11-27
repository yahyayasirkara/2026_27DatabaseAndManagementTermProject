from flask import Blueprint, jsonify, request
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
service = AuthService()


@auth_bp.route('/kayit', methods=['POST'])
def kayit():
    return jsonify(service.kayit(request.get_json(silent=True))), 201


@auth_bp.route('/giris', methods=['POST'])
def giris():
    return jsonify(service.giris(request.get_json(silent=True))), 200
