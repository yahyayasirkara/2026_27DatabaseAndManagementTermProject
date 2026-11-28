from app.entities.base_entity import Entity


class Konaklama(Entity):
    ALANLAR = ("id", "rezervasyon_id", "gercek_giris_zamani", "gercek_cikis_zamani","giris_yapan_personel_id", "cikis_yapan_personel_id", "toplam_tutar", "misafir_id", "oda_id", "giris_tarihi", "cikis_tarihi", "oda_numarasi", "misafir_ad_soyad")
