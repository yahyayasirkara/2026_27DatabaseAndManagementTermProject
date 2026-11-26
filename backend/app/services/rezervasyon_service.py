import mysql.connector
from datetime import date
from app.repositories.rezervasyon_repository import RezervasyonRepository

class RezervasyonService:
    def __init__(self):
        self.repo = RezervasyonRepository()

    def _tarih_dogrula(self, giris_str, cikis_str):
        try:
            giris = date.fromisoformat(giris_str)
            cikis = date.fromisoformat(cikis_str)
        except (TypeError, ValueError):
            return {"hata": "Tarihler YYYY-AA-GG formatında olmalıdır."}, 400
        if cikis <= giris:
            return {"hata": "Çıkış tarihi, giriş tarihinden sonra olmalıdır."}, 400
        return None

    def rezervasyon_olustur(self, veri):
        giris_str = veri.get('giris_tarihi')
        cikis_str = veri.get('cikis_tarihi')
        hata = self._tarih_dogrula(giris_str, cikis_str)
        if hata:
            return hata

        try:
            yeni_id = self.repo.ekle(
                misafir_id=veri.get('misafir_id'),
                oda_id=veri.get('oda_id'),
                giris_tarihi=giris_str,
                cikis_tarihi=cikis_str,
                kisi_sayisi=int(veri.get('kisi_sayisi', 1)),
                durum=veri.get('durum', 'beklemede')
            )
            return {"mesaj": "Rezervasyon başarıyla oluşturuldu", "id": yeni_id}, 201
        except mysql.connector.Error as err:
            if err.errno == 45001:
                return {"hata": err.msg}, 409
            if err.errno == 45002:
                return {"hata": err.msg}, 400
            return {"hata": f"Veritabanı hatası: {err.msg}"}, 500

    def rezervasyon_guncelle(self, rezervasyon_id, veri):
        giris_str = veri.get('giris_tarihi')
        cikis_str = veri.get('cikis_tarihi')
        hata = self._tarih_dogrula(giris_str, cikis_str)
        if hata:
            return hata

        try:
            guncellendi = self.repo.guncelle(
                rezervasyon_id=rezervasyon_id,
                misafir_id=veri.get('misafir_id'),
                oda_id=veri.get('oda_id'),
                giris_tarihi=giris_str,
                cikis_tarihi=cikis_str,
                kisi_sayisi=int(veri.get('kisi_sayisi', 1)),
                durum=veri.get('durum', 'beklemede')
            )
            if not guncellendi:
                return {"hata": "Rezervasyon bulunamadı"}, 404
            return {"mesaj": "Rezervasyon başarıyla güncellendi"}, 200
        except mysql.connector.Error as err:
            if err.errno == 45001:
                return {"hata": err.msg}, 409
            if err.errno == 45002:
                return {"hata": err.msg}, 400
            return {"hata": f"Veritabanı hatası: {err.msg}"}, 500