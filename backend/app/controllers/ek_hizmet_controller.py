from flask import Blueprint, jsonify, request
from app.security.decorators import role_required, PERSONEL_ROLLERI, YONETICI
from app.services.ek_hizmet_service import EkHizmetService

ek_hizmet_bp = Blueprint('ek_hizmet', __name__, url_prefix='/api/ek-hizmetler')
service = EkHizmetService()


@ek_hizmet_bp.route('/', methods=['GET'])
@role_required(*PERSONEL_ROLLERI)
def ek_hizmetleri_getir():
    return jsonify(service.listele()), 200


@ek_hizmet_bp.route('/<int:hizmet_id>', methods=['GET'])
@role_required(*PERSONEL_ROLLERI)
def ek_hizmet_detay(hizmet_id):
    return jsonify(service.getir(hizmet_id)), 200


@ek_hizmet_bp.route('/', methods=['POST'])
@role_required(YONETICI)
def ek_hizmet_ekle():
    return jsonify(service.ekle(request.get_json(silent=True))), 201


@ek_hizmet_bp.route('/<int:hizmet_id>', methods=['PUT'])
@role_required(YONETICI)
def ek_hizmet_guncelle(hizmet_id):
    return jsonify(service.guncelle(hizmet_id, request.get_json(silent=True))), 200


@ek_hizmet_bp.route('/<int:hizmet_id>', methods=['DELETE'])
@role_required(YONETICI)
def ek_hizmet_sil(hizmet_id):
    return jsonify(service.sil(hizmet_id)), 200
