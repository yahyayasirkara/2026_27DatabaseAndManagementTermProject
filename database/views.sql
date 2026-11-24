-- views.sql
-- Sıra: schema.sql -> triggers.sql -> procedures.sql -> views.sql

USE Otel_DB;

-- 1) Bugün giriş ve çıkış yapacak misafirler
-- islem_turu: 'giriş' veya 'çıkış'
-- durum: resepsiyonun o misafir için yapacağı iş (check-in / check-out bekliyor ya da tamamlandı)
CREATE OR REPLACE VIEW vw_bugun_giris_cikis AS
SELECT 'giriş' AS islem_turu,
       Rezervasyon.id AS rezervasyon_id,
       Konaklama.id AS konaklama_id,
       Misafir.ad,
       Misafir.soyad,
       Misafir.telefon,
       Oda.oda_numarasi,
       OdaTipi.tip_adi,
       Rezervasyon.giris_tarihi,
       Rezervasyon.cikis_tarihi,
       Rezervasyon.kisi_sayisi,
       CASE WHEN Konaklama.id IS NULL THEN 'check-in bekliyor' ELSE 'giriş yapıldı' END AS durum
FROM Rezervasyon
JOIN Misafir ON Misafir.id = Rezervasyon.misafir_id
JOIN Oda ON Oda.id = Rezervasyon.oda_id
JOIN OdaTipi ON OdaTipi.id = Oda.oda_tipi_id
LEFT JOIN Konaklama ON Konaklama.rezervasyon_id = Rezervasyon.id
WHERE Rezervasyon.giris_tarihi = CURDATE()
  AND Rezervasyon.durum IN ('onaylı', 'tamamlandı')

UNION ALL

SELECT 'çıkış' AS islem_turu,
       Rezervasyon.id AS rezervasyon_id,
       Konaklama.id AS konaklama_id,
       Misafir.ad,
       Misafir.soyad,
       Misafir.telefon,
       Oda.oda_numarasi,
       OdaTipi.tip_adi,
       Rezervasyon.giris_tarihi,
       Rezervasyon.cikis_tarihi,
       Rezervasyon.kisi_sayisi,
       CASE WHEN Konaklama.gercek_cikis_zamani IS NULL THEN 'check-out bekliyor' ELSE 'çıkış yapıldı' END AS durum
FROM Konaklama
JOIN Rezervasyon ON Rezervasyon.id = Konaklama.rezervasyon_id
JOIN Misafir ON Misafir.id = Rezervasyon.misafir_id
JOIN Oda ON Oda.id = Rezervasyon.oda_id
JOIN OdaTipi ON OdaTipi.id = Oda.oda_tipi_id
WHERE Rezervasyon.cikis_tarihi = CURDATE();


-- 2) Oda bazında güncel durum ve son temizlik tarihi
-- Hiç temizlik kaydı olmayan odada son_temizlik_tarihi NULL gelir.
CREATE OR REPLACE VIEW vw_oda_durum_ozeti AS
SELECT Oda.id AS oda_id,
       Oda.oda_numarasi,
       Oda.kat,
       OdaTipi.tip_adi,
       Oda.durum,
       (SELECT MAX(TemizlikKaydi.tarih)
        FROM TemizlikKaydi
        WHERE TemizlikKaydi.oda_id = Oda.id) AS son_temizlik_tarihi
FROM Oda
JOIN OdaTipi ON OdaTipi.id = Oda.oda_tipi_id;

-- Kontrol: SHOW FULL TABLES IN Otel_DB WHERE Table_type = 'VIEW';   -- 2 view
