from app.entities.base_entity import Entity


class Kullanici(Entity):
    ALANLAR = ("id", "kullanici_adi", "sifre_hash", "rol", "misafir_id", "personel_id")
    GIZLI = ("sifre_hash",)
