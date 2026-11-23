import os
import mysql.connector
from app.entities.oda_tipi import OdaTipi

class OdaTipiRepository:
    def get_db_connection(self):
        # Ayarları config.py yerine doğrudan .env dosyasından güvenle okuyoruz
        return mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'otel_db')
        )

    def tum_oda_tiplerini_getir(self):
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, tip_adi, aciklama, kapasite, temel_fiyat FROM OdaTipi")
        rows = cursor.fetchall()
        
        oda_tipleri = []
        for row in rows:
            oda_tipi = OdaTipi(
                id=row['id'],
                ad=row['tip_adi'], 
                aciklama=row['aciklama'],
                kapasite=row['kapasite'],
                taban_fiyat=row['temel_fiyat']
            )
            oda_tipleri.append(oda_tipi)
            
        cursor.close()
        conn.close()
        return oda_tipleri