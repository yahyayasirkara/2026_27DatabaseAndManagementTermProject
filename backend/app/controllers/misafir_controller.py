import mysql.connector
from flask import Blueprint, jsonify, request
from app.repositories.misafir_repository import MisafirRepository

misafir_bp = Blueprint('misafir', __name__, url_prefix='/api/misafirler')
repo = MisafirRepository()

@misafir_bp.route('/', methods=['GET'])
def misafirleri_getir():
    tc = request.args.get('tc')
    if tc:
        misafir = repo.tc_ile_ara(tc)
        if not misafir:
            return jsonify({"hata": "Misafir bulunamadı"}), 404
        return jsonify(misafir.to_dict()), 200
    misafirler = repo.tumunu_getir()
    return jsonify([m.to_dict() for m in misafirler]), 200

@misafir_bp.route('/<int:misafir_id>', methods=['GET'])
def misafir_detay(misafir_id):
    misafir = repo.id_ile_getir(misafir_id)
    if not misafir:
        return jsonify({"hata": "Misafir bulunamadı"}), 404
    return jsonify(misafir.to_dict()), 200

@misafir_bp.route('/', methods=['POST'])
def misafir_ekle():
    veri = request.get_json()
    try:
        yeni_id = repo.ekle(
            veri['ad'], veri['soyad'], veri['tc_pasaport_no'],
            veri['telefon'], veri.get('eposta'), veri.get('dogum_tarihi')
        )
        return jsonify({"mesaj": "Misafir eklendi", "id": yeni_id}), 201
    except mysql.connector.Error as err:
        return jsonify({"hata": err.msg}), 400

@misafir_bp.route('/<int:misafir_id>', methods=['PUT'])
def misafir_guncelle(misafir_id):
    veri = request.get_json()
    try:
        guncellendi = repo.guncelle(
            misafir_id, veri['ad'], veri['soyad'], veri['tc_pasaport_no'],
            veri['telefon'], veri.get('eposta'), veri.get('dogum_tarihi')
        )
        if not guncellendi:
            return jsonify({"hata": "Misafir bulunamadı"}), 404
        return jsonify({"mesaj": "Misafir güncellendi"}), 200
    except mysql.connector.Error as err:
        return jsonify({"hata": err.msg}), 400

@misafir_bp.route('/<int:misafir_id>', methods=['DELETE'])
def misafir_sil(misafir_id):
    try:
        silindi = repo.sil(misafir_id)
        if not silindi:
            return jsonify({"hata": "Misafir bulunamadı"}), 404
        return jsonify({"mesaj": "Misafir silindi"}), 200
    except mysql.connector.Error as err:
        return jsonify({"hata": f"Misafir silinemedi: {err.msg}"}), 409