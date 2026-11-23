from flask import Blueprint, jsonify, request
from app.repositories.misafir_repository import MisafirRepository

misafir_bp = Blueprint('misafir', __name__, url_prefix='/api/misafirler')
repo = MisafirRepository()

@misafir_bp.route('/', methods=['GET'])
def misafirleri_getir():
    misafirler = repo.tumunu_getir()
    return jsonify([m.to_dict() for m in misafirler]), 200

@misafir_bp.route('/', methods=['POST'])
def misafir_ekle():
    veri = request.get_json()
    yeni_id = repo.ekle(
        ad=veri['ad'],
        soyad=veri['soyad'],
        tc_pasaport_no=veri['tc_pasaport_no'],
        telefon=veri['telefon'],
        eposta=veri['eposta'],
        dogum_tarihi=veri['dogum_tarihi']
    )
    return jsonify({"mesaj": "Misafir başarıyla eklendi", "id": yeni_id}), 201