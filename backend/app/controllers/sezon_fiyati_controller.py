from flask import Blueprint, jsonify, request
from app.security.decorators import role_required, YONETICI
from app.services.sezon_fiyati_service import SezonFiyatiService

sezon_fiyati_bp = Blueprint('sezon_fiyati', __name__, url_prefix='/api/sezon-fiyatlari')
service = SezonFiyatiService()


@sezon_fiyati_bp.route('/', methods=['GET'])
@role_required()
def sezon_fiyatlarini_getir():
    return jsonify(service.listele(request.args.get('oda_tipi_id', type=int))), 200


@sezon_fiyati_bp.route('/<int:sezon_id>', methods=['GET'])
@role_required()
def sezon_fiyati_detay(sezon_id):
    return jsonify(service.getir(sezon_id)), 200


@sezon_fiyati_bp.route('/', methods=['POST'])
@role_required(YONETICI)
def sezon_fiyati_ekle():
    return jsonify(service.ekle(request.get_json(silent=True))), 201


@sezon_fiyati_bp.route('/<int:sezon_id>', methods=['PUT'])
@role_required(YONETICI)
def sezon_fiyati_guncelle(sezon_id):
    return jsonify(service.guncelle(sezon_id, request.get_json(silent=True))), 200


@sezon_fiyati_bp.route('/<int:sezon_id>', methods=['DELETE'])
@role_required(YONETICI)
def sezon_fiyati_sil(sezon_id):
    return jsonify(service.sil(sezon_id)), 200
