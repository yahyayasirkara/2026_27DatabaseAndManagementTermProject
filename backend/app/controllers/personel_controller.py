from flask import Blueprint, jsonify, request
from app.security.decorators import role_required, YONETICI
from app.services.personel_service import PersonelService

personel_bp = Blueprint('personel', __name__, url_prefix='/api/personel')
service = PersonelService()


@personel_bp.route('/', methods=['GET'])
@role_required(YONETICI)
def personelleri_getir():
    return jsonify(service.listele()), 200


@personel_bp.route('/<int:personel_id>', methods=['GET'])
@role_required(YONETICI)
def personel_detay(personel_id):
    return jsonify(service.getir(personel_id)), 200


@personel_bp.route('/', methods=['POST'])
@role_required(YONETICI)
def personel_ekle():
    return jsonify(service.ekle(request.get_json(silent=True))), 201


@personel_bp.route('/<int:personel_id>', methods=['PUT'])
@role_required(YONETICI)
def personel_guncelle(personel_id):
    return jsonify(service.guncelle(personel_id, request.get_json(silent=True))), 200


@personel_bp.route('/<int:personel_id>', methods=['DELETE'])
@role_required(YONETICI)
def personel_sil(personel_id):
    return jsonify(service.sil(personel_id)), 200
