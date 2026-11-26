import mysql.connector
from flask import current_app
from app.entities.oda_tipi import OdaTipi

class OdaTipiRepository:
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
            cursor.execute("SELECT * FROM OdaTipi ORDER BY id ASC")
            return [OdaTipi(**satir) for satir in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def id_ile_getir(self, oda_tipi_id):
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM OdaTipi WHERE id = %s", (oda_tipi_id,))
            satir = cursor.fetchone()
            return OdaTipi(**satir) if satir else None
        finally:
            cursor.close()
            conn.close()

    def ekle(self, tip_adi, kapasite, aciklama, temel_fiyat):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            sorgu = "INSERT INTO OdaTipi (tip_adi, kapasite, aciklama, temel_fiyat) VALUES (%s, %s, %s, %s)"
            cursor.execute(sorgu, (tip_adi, kapasite, aciklama, temel_fiyat))
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def guncelle(self, oda_tipi_id, tip_adi, kapasite, aciklama, temel_fiyat):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            sorgu = """
                UPDATE OdaTipi
                SET tip_adi = %s, kapasite = %s, aciklama = %s, temel_fiyat = %s
                WHERE id = %s
            """
            cursor.execute(sorgu, (tip_adi, kapasite, aciklama, temel_fiyat, oda_tipi_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def sil(self, oda_tipi_id):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM OdaTipi WHERE id = %s", (oda_tipi_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()