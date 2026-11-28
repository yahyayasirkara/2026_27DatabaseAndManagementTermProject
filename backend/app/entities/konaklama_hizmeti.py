from app.entities.base_entity import Entity


class KonaklamaHizmeti(Entity):
    ALANLAR = ("id", "konaklama_id", "ek_hizmet_id", "adet", "birim_fiyat", "tarih", "hizmet_adi")
