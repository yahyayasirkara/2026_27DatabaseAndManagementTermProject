import os
import mysql.connector
from app.entities.rezervasyon import Rezervasyon

class RezervasyonRepository:
    def get_db_connection(self):
        return mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'otel_db')
        )

    def tumunu_getir(self):
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sorgu = """
                SELECT r.id, r.misafir_id, r.oda_id, r.giris_tarihi, r.cikis_tarihi,
                       r.kisi_sayisi, r.durum, r.olusturma_tarihi,
                       CONCAT(m.ad, ' ', m.soyad) AS misafir_ad_soyad,
                       o.oda_numarasi
                FROM Rezervasyon r
                JOIN Misafir m ON r.misafir_id = m.id
                JOIN Oda o ON r.oda_id = o.id
                ORDER BY r.olusturma_tarihi DESC
            """
            cursor.execute(sorgu)
            satirlar = cursor.fetchall()
            return [
                Rezervasyon(
                    id=s['id'],
                    misafir_id=s['misafir_id'],
                    oda_id=s['oda_id'],
                    giris_tarihi=s['giris_tarihi'],
                    cikis_tarihi=s['cikis_tarihi'],
                    kisi_sayisi=s['kisi_sayisi'],
                    durum=s['durum'],
                    olusturma_tarihi=s['olusturma_tarihi'],
                    misafir_ad_soyad=s['misafir_ad_soyad'],
                    oda_numarasi=s['oda_numarasi']
                )
                for s in satirlar
            ]
        finally:
            cursor.close()
            conn.close()

    def ekle(self, misafir_id, oda_id, giris_tarihi, cikis_tarihi, kisi_sayisi, durum="beklemede"):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            sorgu = """
                INSERT INTO Rezervasyon (misafir_id, oda_id, giris_tarihi, cikis_tarihi, kisi_sayisi, durum)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sorgu, (misafir_id, oda_id, giris_tarihi, cikis_tarihi, kisi_sayisi, durum))
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()

    def durum_guncelle(self, rezervasyon_id, yeni_durum):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            sorgu = "UPDATE Rezervasyon SET durum = %s WHERE id = %s"
            cursor.execute(sorgu, (yeni_durum, rezervasyon_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()