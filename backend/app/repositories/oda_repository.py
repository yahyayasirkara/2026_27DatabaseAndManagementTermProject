import os
import mysql.connector
from app.entities.oda import Oda

class OdaRepository:
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
                SELECT o.id, o.oda_numarasi, o.kat, o.oda_tipi_id, o.durum,
                       ot.tip_adi, ot.temel_fiyat
                FROM Oda o
                JOIN OdaTipi ot ON o.oda_tipi_id = ot.id
                ORDER BY o.oda_numarasi ASC
            """
            cursor.execute(sorgu)
            satirlar = cursor.fetchall()
            return [
                Oda(
                    id=s['id'],
                    oda_numarasi=s['oda_numarasi'],
                    kat=s['kat'],
                    oda_tipi_id=s['oda_tipi_id'],
                    durum=s['durum'],
                    tip_adi=s['tip_adi'],
                    temel_fiyat=s['temel_fiyat']
                )
                for s in satirlar
            ]
        finally:
            cursor.close()
            conn.close()

    def ekle(self, oda_numarasi, kat, oda_tipi_id, durum="boş"):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            sorgu = """
                INSERT INTO Oda (oda_numarasi, kat, oda_tipi_id, durum)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sorgu, (oda_numarasi, kat, oda_tipi_id, durum))
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()

    def durum_guncelle(self, oda_id, yeni_durum):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            sorgu = "UPDATE Oda SET durum = %s WHERE id = %s"
            cursor.execute(sorgu, (yeni_durum, oda_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()