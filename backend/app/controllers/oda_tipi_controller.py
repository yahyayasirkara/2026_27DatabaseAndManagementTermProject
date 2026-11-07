from flask import Blueprint, jsonify
from app.repositories.oda_tipi_repository import OdaTipiRepository

# '/api/oda-tipleri' adresine gelen istekleri bu Blueprint yönetecek
oda_tipi_bp = Blueprint('oda_tipi', __name__, url_prefix='/api/oda-tipleri')
repo = OdaTipiRepository()

@oda_tipi_bp.route('/', methods=['GET'])
def get_oda_tipleri():
    """Tüm oda tiplerini veritabanından çekip JSON olarak döndürür."""
    oda_tipleri = repo.tum_oda_tiplerini_getir()
    
    # Gelen nesne listesini JSON formatına (to_dict) çeviriyoruz
    sonuc = [oda.to_dict() for oda in oda_tipleri]
    
    return jsonify(sonuc), 200