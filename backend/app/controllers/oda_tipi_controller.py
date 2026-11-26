import mysql.connector
from flask import Blueprint, jsonify, request
from app.repositories.oda_tipi_repository import OdaTipiRepository

oda_tipi_bp = Blueprint('oda_tipi', __name__, url_prefix='/api/oda-tipleri')
repo = OdaTipiRepository()

@oda_tipi_bp.route('/', methods=['GET'])
def oda_tiplerini_getir():
    tipler = repo.tumunu_getir()
    return jsonify([t.to_dict() for t in tipler]), 200

@oda_tipi_bp.route('/<int:oda_tipi_id>', methods=['GET'])
def oda_tipi_detay(oda_tipi_id):
    tip = repo.id_ile_getir(oda_tipi_id)
    if not tip:
        return jsonify({"hata": "Oda tipi bulunamadı"}), 404
    return jsonify(tip.to_dict()), 200

@oda_tipi_bp.route('/', methods=['POST'])
def oda_tipi_ekle():
    veri = request.get_json()
    try:
        yeni_id = repo.ekle(veri['tip_adi'], veri['kapasite'], veri.get('aciklama'), veri['temel_fiyat'])
        return jsonify({"mesaj": "Oda tipi eklendi", "id": yeni_id}), 201
    except mysql.connector.Error as err:
        return jsonify({"hata": err.msg}), 400

@oda_tipi_bp.route('/<int:oda_tipi_id>', methods=['PUT'])
def oda_tipi_guncelle(oda_tipi_id):
    veri = request.get_json()
    try:
        guncellendi = repo.guncelle(oda_tipi_id, veri['tip_adi'], veri['kapasite'], veri.get('aciklama'), veri['temel_fiyat'])
        if not guncellendi:
            return jsonify({"hata": "Oda tipi bulunamadı"}), 404
        return jsonify({"mesaj": "Oda tipi güncellendi"}), 200
    except mysql.connector.Error as err:
        return jsonify({"hata": err.msg}), 400

@oda_tipi_bp.route('/<int:oda_tipi_id>', methods=['DELETE'])
def oda_tipi_sil(oda_tipi_id):
    try:
        silindi = repo.sil(oda_tipi_id)
        if not silindi:
            return jsonify({"hata": "Oda tipi bulunamadı"}), 404
        return jsonify({"mesaj": "Oda tipi silindi"}), 200
    except mysql.connector.Error as err:
        return jsonify({"hata": f"Silinemedi (bağlı kayıtlar olabilir): {err.msg}"}), 409