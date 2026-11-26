from flask import Blueprint, jsonify, request
from app.repositories.rezervasyon_repository import RezervasyonRepository
from app.services.rezervasyon_service import RezervasyonService

rezervasyon_bp = Blueprint('rezervasyon', __name__, url_prefix='/api/rezervasyonlar')
repo = RezervasyonRepository()
service = RezervasyonService()

@rezervasyon_bp.route('/', methods=['GET'])
def rezervasyonlari_getir():
    rezervasyonlar = repo.tumunu_getir()
    return jsonify([r.to_dict() for r in rezervasyonlar]), 200

@rezervasyon_bp.route('/', methods=['POST'])
def rezervasyon_ekle():
    veri = request.get_json()
    sonuc, durum_kodu = service.rezervasyon_olustur(veri)
    return jsonify(sonuc), durum_kodu

@rezervasyon_bp.route('/<int:rezervasyon_id>/durum', methods=['PATCH'])
def rezervasyon_durum_guncelle(rezervasyon_id):
    veri = request.get_json()
    guncellendi = repo.durum_guncelle(rezervasyon_id, veri['durum'])
    if not guncellendi:
        return jsonify({"hata": "Rezervasyon bulunamadı"}), 404
    return jsonify({"mesaj": "Rezervasyon durumu güncellendi"}), 200