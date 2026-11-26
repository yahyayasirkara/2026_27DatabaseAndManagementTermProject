import mysql.connector
from flask import current_app
from app.entities.rezervasyon import Rezervasyon

class RezervasyonRepository:
    def get_db_connection(self):
        return mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB']
        )

    def tumunu_getir(self):
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sorgu = """
                SELECT r.*, CONCAT(m.ad, ' ', m.soyad) AS misafir_ad_soyad, o.oda_numarasi
                FROM Rezervasyon r
                JOIN Misafir m ON r.misafir_id = m.id
                JOIN Oda o ON r.oda_id = o.id
                ORDER BY r.id DESC
            """
            cursor.execute(sorgu)
            return [Rezervasyon(**satir) for satir in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def id_ile_getir(self, rezervasyon_id):
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sorgu = """
                SELECT r.*, CONCAT(m.ad, ' ', m.soyad) AS misafir_ad_soyad, o.oda_numarasi
                FROM Rezervasyon r
                JOIN Misafir m ON r.misafir_id = m.id
                JOIN Oda o ON r.oda_id = o.id
                WHERE r.id = %s
            """
            cursor.execute(sorgu, (rezervasyon_id,))
            satir = cursor.fetchone()
            return Rezervasyon(**satir) if satir else None
        finally:
            cursor.close()
            conn.close()

    def musait_odalari_getir(self, giris_tarihi, cikis_tarihi, oda_tipi_id=None):
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Arkadaşının procedures.sql içinde yazdığı sp_musait_odalar prosedürünü çağırır
            cursor.callproc('sp_musait_odalar', [giris_tarihi, cikis_tarihi, oda_tipi_id])
            sonuclar = []
            for result in cursor.stored_results():
                for satir in result.fetchall():
                    # Decimal fiyat varsa JSON uyumu için float'a çevir
                    for k, v in satir.items():
                        if hasattr(v, '__float__') and not isinstance(v, (int, float)):
                            satir[k] = float(v)
                    sonuclar.append(satir)
            return sonuclar
        finally:
            cursor.close()
            conn.close()

    def ekle(self, misafir_id, oda_id, giris_tarihi, cikis_tarihi, kisi_sayisi, durum='beklemede'):
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
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def guncelle(self, rezervasyon_id, misafir_id, oda_id, giris_tarihi, cikis_tarihi, kisi_sayisi, durum):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            sorgu = """
                UPDATE Rezervasyon
                SET misafir_id = %s, oda_id = %s, giris_tarihi = %s, cikis_tarihi = %s, kisi_sayisi = %s, durum = %s
                WHERE id = %s
            """
            cursor.execute(sorgu, (misafir_id, oda_id, giris_tarihi, cikis_tarihi, kisi_sayisi, durum, rezervasyon_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def durum_guncelle(self, rezervasyon_id, yeni_durum):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE Rezervasyon SET durum = %s WHERE id = %s", (yeni_durum, rezervasyon_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def sil(self, rezervasyon_id):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Rezervasyon WHERE id = %s", (rezervasyon_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()