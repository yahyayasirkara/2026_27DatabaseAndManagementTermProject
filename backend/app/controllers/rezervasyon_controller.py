from flask import Blueprint, jsonify, request
from app.repositories.rezervasyon_repository import RezervasyonRepository

rezervasyon_bp = Blueprint('rezervasyon', __name__, url_prefix='/api/rezervasyonlar')
repo = RezervasyonRepository()

@rezervasyon_bp.route('/', methods=['GET'])
def rezervasyonlari_getir():
    rezervasyonlar = repo.tumunu_getir()
    return jsonify([r.to_dict() for r in rezervasyonlar]), 200

@rezervasyon_bp.route('/', methods=['POST'])
def rezervasyon_ekle():
    veri = request.get_json()
    yeni_id = repo.ekle(
        misafir_id=veri['misafir_id'],
        oda_id=veri['oda_id'],
        giris_tarihi=veri['giris_tarihi'],
        cikis_tarihi=veri['cikis_tarihi'],
        kisi_sayisi=veri['kisi_sayisi'],
        durum=veri.get('durum', 'beklemede')
    )
    return jsonify({"mesaj": "Rezervasyon oluşturuldu", "id": yeni_id}), 201

@rezervasyon_bp.route('/<int:rezervasyon_id>/durum', methods=['PATCH'])
def rezervasyon_durum_guncelle(rezervasyon_id):
    veri = request.get_json()
    guncellendi = repo.durum_guncelle(rezervasyon_id, veri['durum'])
    if not guncellendi:
        return jsonify({"hata": "Rezervasyon bulunamadı"}), 404
    return jsonify({"mesaj": "Rezervasyon durumu güncellendi"}), 200