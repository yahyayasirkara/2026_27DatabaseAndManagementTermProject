import mysql.connector
from flask import Blueprint, jsonify, request
from app.repositories.oda_repository import OdaRepository

oda_bp = Blueprint('oda', __name__, url_prefix='/api/odalar')
repo = OdaRepository()

@oda_bp.route('/', methods=['GET'])
def odalari_getir():
    odalar = repo.tumunu_getir()
    return jsonify([o.to_dict() for o in odalar]), 200

@oda_bp.route('/<int:oda_id>', methods=['GET'])
def oda_detay(oda_id):
    oda = repo.id_ile_getir(oda_id)
    if not oda:
        return jsonify({"hata": "Oda bulunamadı"}), 404
    return jsonify(oda.to_dict()), 200

@oda_bp.route('/', methods=['POST'])
def oda_ekle():
    veri = request.get_json()
    try:
        yeni_id = repo.ekle(veri['oda_numarasi'], veri['kat'], veri['oda_tipi_id'], veri.get('durum', 'boş'))
        return jsonify({"mesaj": "Oda eklendi", "id": yeni_id}), 201
    except mysql.connector.Error as err:
        return jsonify({"hata": err.msg}), 400

@oda_bp.route('/<int:oda_id>', methods=['PUT'])
def oda_guncelle(oda_id):
    veri = request.get_json()
    try:
        guncellendi = repo.guncelle(oda_id, veri['oda_numarasi'], veri['kat'], veri['oda_tipi_id'], veri['durum'])
        if not guncellendi:
            return jsonify({"hata": "Oda bulunamadı"}), 404
        return jsonify({"mesaj": "Oda güncellendi"}), 200
    except mysql.connector.Error as err:
        return jsonify({"hata": err.msg}), 400

@oda_bp.route('/<int:oda_id>/durum', methods=['PATCH'])
def oda_durum_guncelle(oda_id):
    veri = request.get_json()
    try:
        guncellendi = repo.durum_guncelle(oda_id, veri['durum'])
        if not guncellendi:
            return jsonify({"hata": "Oda bulunamadı"}), 404
        return jsonify({"mesaj": "Oda durumu güncellendi"}), 200
    except mysql.connector.Error as err:
        return jsonify({"hata": err.msg}), 400

@oda_bp.route('/<int:oda_id>', methods=['DELETE'])
def oda_sil(oda_id):
    try:
        silindi = repo.sil(oda_id)
        if not silindi:
            return jsonify({"hata": "Oda bulunamadı"}), 404
        return jsonify({"mesaj": "Oda silindi"}), 200
    except mysql.connector.Error as err:
        return jsonify({"hata": f"Oda silinemedi: {err.msg}"}), 409