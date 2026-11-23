import os
import mysql.connector
from app.entities.misafir import Misafir

class MisafirRepository:
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
            cursor.execute("SELECT * FROM Misafir")
            satirlar = cursor.fetchall()
            return [
                Misafir(
                    id=satir['id'],
                    ad=satir['ad'],
                    soyad=satir['soyad'],
                    tc_pasaport_no=satir['tc_pasaport_no'],
                    telefon=satir['telefon'],
                    eposta=satir['eposta'],
                    dogum_tarihi=satir['dogum_tarihi']
                )
                for satir in satirlar
            ]
        finally:
            cursor.close()
            conn.close()

    def ekle(self, ad, soyad, tc_pasaport_no, telefon, eposta, dogum_tarihi):
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
        finally:
            cursor.close()
            conn.close()