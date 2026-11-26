import mysql.connector
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

@rezervasyon_bp.route('/<int:rezervasyon_id>', methods=['GET'])
def rezervasyon_detay(rezervasyon_id):
    rez = repo.id_ile_getir(rezervasyon_id)
    if not rez:
        return jsonify({"hata": "Rezervasyon bulunamadı"}), 404
    return jsonify(rez.to_dict()), 200

@rezervasyon_bp.route('/musait-odalar', methods=['GET'])
def musait_odalari_getir():
    giris = request.args.get('giris')
    cikis = request.args.get('cikis')
    tip_id = request.args.get('oda_tipi_id', type=int)
    if not giris or not cikis:
        return jsonify({"hata": "giris ve cikis parametreleri zorunludur (?giris=YYYY-AA-GG&cikis=YYYY-AA-GG)"}), 400
    try:
        odalar = repo.musait_odalari_getir(giris, cikis, tip_id)
        return jsonify(odalar), 200
    except mysql.connector.Error as err:
        return jsonify({"hata": err.msg}), 400

@rezervasyon_bp.route('/', methods=['POST'])
def rezervasyon_ekle():
    veri = request.get_json()
    sonuc, durum_kodu = service.rezervasyon_olustur(veri)
    return jsonify(sonuc), durum_kodu

@rezervasyon_bp.route('/<int:rezervasyon_id>', methods=['PUT'])
def rezervasyon_guncelle(rezervasyon_id):
    veri = request.get_json()
    sonuc, durum_kodu = service.rezervasyon_guncelle(rezervasyon_id, veri)
    return jsonify(sonuc), durum_kodu

@rezervasyon_bp.route('/<int:rezervasyon_id>/durum', methods=['PATCH'])
def rezervasyon_durum_guncelle(rezervasyon_id):
    veri = request.get_json()
    try:
        guncellendi = repo.durum_guncelle(rezervasyon_id, veri['durum'])
        if not guncellendi:
            return jsonify({"hata": "Rezervasyon bulunamadı"}), 404
        return jsonify({"mesaj": "Rezervasyon durumu güncellendi"}), 200
    except mysql.connector.Error as err:
        if err.errno == 45001:
            return jsonify({"hata": err.msg}), 409
        if err.errno == 45002:
            return jsonify({"hata": err.msg}), 400
        return jsonify({"hata": err.msg}), 500

@rezervasyon_bp.route('/<int:rezervasyon_id>', methods=['DELETE'])
def rezervasyon_sil(rezervasyon_id):
    try:
        silindi = repo.sil(rezervasyon_id)
        if not silindi:
            return jsonify({"hata": "Rezervasyon bulunamadı"}), 404
        return jsonify({"mesaj": "Rezervasyon silindi"}), 200
    except mysql.connector.Error as err:
        return jsonify({"hata": f"Rezervasyon silinemedi: {err.msg}"}), 409