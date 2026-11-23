from flask import Blueprint, jsonify, request
from app.repositories.oda_repository import OdaRepository

oda_bp = Blueprint('oda', __name__, url_prefix='/api/odalar')
repo = OdaRepository()

@oda_bp.route('/', methods=['GET'])
def odalari_getir():
    odalar = repo.tumunu_getir()
    return jsonify([o.to_dict() for o in odalar]), 200

@oda_bp.route('/', methods=['POST'])
def oda_ekle():
    veri = request.get_json()
    yeni_id = repo.ekle(
        oda_numarasi=veri['oda_numarasi'],
        kat=veri['kat'],
        oda_tipi_id=veri['oda_tipi_id'],
        durum=veri.get('durum', 'boş')
    )
    return jsonify({"mesaj": "Oda başarıyla eklendi", "id": yeni_id}), 201

@oda_bp.route('/<int:oda_id>/durum', methods=['PATCH'])
def oda_durum_guncelle(oda_id):
    veri = request.get_json()
    guncellendi = repo.durum_guncelle(oda_id, veri['durum'])
    if not guncellendi:
        return jsonify({"hata": "Oda bulunamadı"}), 404
    return jsonify({"mesaj": "Oda durumu güncellendi"}), 200