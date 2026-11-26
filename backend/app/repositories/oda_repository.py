import mysql.connector
from flask import current_app
from app.entities.oda import Oda

class OdaRepository:
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
                SELECT o.*, ot.tip_adi, ot.kapasite, ot.temel_fiyat
                FROM Oda o
                JOIN OdaTipi ot ON o.oda_tipi_id = ot.id
                ORDER BY o.oda_numarasi ASC
            """
            cursor.execute(sorgu)
            return [Oda(**satir) for satir in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def id_ile_getir(self, oda_id):
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sorgu = """
                SELECT o.*, ot.tip_adi, ot.kapasite, ot.temel_fiyat
                FROM Oda o
                JOIN OdaTipi ot ON o.oda_tipi_id = ot.id
                WHERE o.id = %s
            """
            cursor.execute(sorgu, (oda_id,))
            satir = cursor.fetchone()
            return Oda(**satir) if satir else None
        finally:
            cursor.close()
            conn.close()

    def ekle(self, oda_numarasi, kat, oda_tipi_id, durum='boş'):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            sorgu = "INSERT INTO Oda (oda_numarasi, kat, oda_tipi_id, durum) VALUES (%s, %s, %s, %s)"
            cursor.execute(sorgu, (oda_numarasi, kat, oda_tipi_id, durum))
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def guncelle(self, oda_id, oda_numarasi, kat, oda_tipi_id, durum):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            sorgu = """
                UPDATE Oda
                SET oda_numarasi = %s, kat = %s, oda_tipi_id = %s, durum = %s
                WHERE id = %s
            """
            cursor.execute(sorgu, (oda_numarasi, kat, oda_tipi_id, durum, oda_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def durum_guncelle(self, oda_id, yeni_durum):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE Oda SET durum = %s WHERE id = %s", (yeni_durum, oda_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def sil(self, oda_id):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Oda WHERE id = %s", (oda_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()