from flask import Blueprint, jsonify, request
from app.security.decorators import role_required, mevcut_kullanici, PERSONEL_ROLLERI
from app.services.konaklama_service import KonaklamaService
from app.services.odeme_service import OdemeService

konaklama_bp = Blueprint('konaklama', __name__, url_prefix='/api/konaklamalar')
service = KonaklamaService()
odeme_service = OdemeService()


@konaklama_bp.route('/', methods=['GET'])
@role_required(*PERSONEL_ROLLERI)
def konaklamalari_getir():
    return jsonify(service.listele(request.args.get('aktif') in ('1', 'true'))), 200


@konaklama_bp.route('/bugun', methods=['GET'])
@role_required(*PERSONEL_ROLLERI)
def bugun_giris_cikis():
    return jsonify(service.gunluk_liste()), 200


@konaklama_bp.route('/gecmis', methods=['GET'])
@role_required()
def gecmis_konaklamalar():
    return jsonify(service.gecmis(mevcut_kullanici(), request.args.get('misafir_id', type=int))), 200


@konaklama_bp.route('/<int:konaklama_id>', methods=['GET'])
@role_required(*PERSONEL_ROLLERI)
def konaklama_detay(konaklama_id):
    return jsonify(service.getir(konaklama_id)), 200


@konaklama_bp.route('/check-in', methods=['POST'])
@role_required(*PERSONEL_ROLLERI)
def check_in():
    return jsonify(service.check_in(request.get_json(silent=True), mevcut_kullanici())), 201


@konaklama_bp.route('/<int:konaklama_id>/hizmetler', methods=['GET'])
@role_required(*PERSONEL_ROLLERI)
def hizmetleri_getir(konaklama_id):
    return jsonify(service.hizmetler(konaklama_id)), 200


@konaklama_bp.route('/<int:konaklama_id>/hizmetler', methods=['POST'])
@role_required(*PERSONEL_ROLLERI)
def hizmet_ekle(konaklama_id):
    return jsonify(service.hizmet_ekle(konaklama_id, request.get_json(silent=True))), 201


@konaklama_bp.route('/<int:konaklama_id>/tutar', methods=['GET'])
@role_required(*PERSONEL_ROLLERI)
def tutar_hesapla(konaklama_id):
    return jsonify(service.tutar(konaklama_id)), 200


@konaklama_bp.route('/<int:konaklama_id>/check-out', methods=['POST'])
@role_required(*PERSONEL_ROLLERI)
def check_out(konaklama_id):
    return jsonify(service.check_out(konaklama_id, request.get_json(silent=True), mevcut_kullanici())), 200


@konaklama_bp.route('/<int:konaklama_id>/odemeler', methods=['GET'])
@role_required(*PERSONEL_ROLLERI)
def odemeleri_getir(konaklama_id):
    return jsonify(odeme_service.konaklamanin_odemeleri(konaklama_id)), 200
