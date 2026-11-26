import mysql.connector
from flask import current_app
from app.entities.misafir import Misafir

class MisafirRepository:
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
            cursor.execute("SELECT * FROM Misafir ORDER BY id DESC")
            return [Misafir(**satir) for satir in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def id_ile_getir(self, misafir_id):
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM Misafir WHERE id = %s", (misafir_id,))
            satir = cursor.fetchone()
            return Misafir(**satir) if satir else None
        finally:
            cursor.close()
            conn.close()

    def tc_ile_ara(self, tc_pasaport_no):
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM Misafir WHERE tc_pasaport_no = %s", (tc_pasaport_no,))
            satir = cursor.fetchone()
            return Misafir(**satir) if satir else None
        finally:
            cursor.close()
            conn.close()

    def ekle(self, ad, soyad, tc_pasaport_no, telefon, eposta=None, dogum_tarihi=None):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            sorgu = """
                INSERT INTO Misafir (ad, soyad, tc_pasaport_no, telefon, eposta, dogum_tarihi)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sorgu, (ad, soyad, tc_pasaport_no, telefon, eposta, dogum_tarihi))
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def guncelle(self, misafir_id, ad, soyad, tc_pasaport_no, telefon, eposta=None, dogum_tarihi=None):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            sorgu = """
                UPDATE Misafir
                SET ad = %s, soyad = %s, tc_pasaport_no = %s, telefon = %s, eposta = %s, dogum_tarihi = %s
                WHERE id = %s
            """
            cursor.execute(sorgu, (ad, soyad, tc_pasaport_no, telefon, eposta, dogum_tarihi, misafir_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def sil(self, misafir_id):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Misafir WHERE id = %s", (misafir_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()