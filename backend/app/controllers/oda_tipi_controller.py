from flask import Blueprint, jsonify
from app.repositories.oda_tipi_repository import OdaTipiRepository

oda_tipi_bp = Blueprint('oda_tipi', __name__, url_prefix='/api/oda-tipleri')
repo = OdaTipiRepository()

@oda_tipi_bp.route('/', methods=['GET'])
def get_oda_tipleri():
    oda_tipleri = repo.tum_oda_tiplerini_getir()
    sonuc = [oda.to_dict() for oda in oda_tipleri]
    return jsonify(sonuc), 200