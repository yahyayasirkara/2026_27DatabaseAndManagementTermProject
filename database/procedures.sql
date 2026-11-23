-- procedures.sql
-- Sıra: schema.sql -> triggers.sql -> procedures.sql -> views.sql
-- Hata kodları: 45001 = iş kuralı ihlali / çakışma, 45002 = geçersiz işlem
-- Not: Parametre ve değişken adları tablo sütunlarıyla aynı olmasın diye özellikle farklı seçildi
-- (MySQL'de aynı ad olursa değişken öncelik alır ve sorgu yanlış çalışır).

USE Otel_DB;

DELIMITER $$

-- 1) Verilen tarih aralığında ve oda tipinde boş odaları listeler.
-- aranan_tip_id NULL gelirse tüm oda tipleri listelenir.
-- Her gece için o geceye ait sezon fiyatı, sezon yoksa oda tipinin temel fiyatı kullanılır.
DROP PROCEDURE IF EXISTS sp_musait_odalar$$
CREATE PROCEDURE sp_musait_odalar(
    IN aranan_giris DATE,
    IN aranan_cikis DATE,
    IN aranan_tip_id INT
)
BEGIN
    IF aranan_giris IS NULL OR aranan_cikis IS NULL OR aranan_cikis <= aranan_giris THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 45002,
            MESSAGE_TEXT = 'Çıkış tarihi giriş tarihinden sonra olmalıdır.';
    END IF;

    IF DATEDIFF(aranan_cikis, aranan_giris) > 365 THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 45002,
            MESSAGE_TEXT = 'En fazla 365 gecelik aralık aranabilir.';
    END IF;

    WITH RECURSIVE geceler AS (
        SELECT aranan_giris AS gece
        UNION ALL
        SELECT DATE_ADD(gece, INTERVAL 1 DAY)
        FROM geceler
        WHERE DATE_ADD(gece, INTERVAL 1 DAY) < aranan_cikis
    ),
    gecelik_fiyatlar AS (
        SELECT OdaTipi.id AS oda_tipi_id,
               COALESCE(
                   (SELECT SezonFiyati.gecelik_fiyat
                    FROM SezonFiyati
                    WHERE SezonFiyati.oda_tipi_id = OdaTipi.id
                      AND geceler.gece BETWEEN SezonFiyati.baslangic_tarihi AND SezonFiyati.bitis_tarihi
                    ORDER BY SezonFiyati.baslangic_tarihi DESC, SezonFiyati.id DESC
                    LIMIT 1),
                   OdaTipi.temel_fiyat
               ) AS fiyat
        FROM OdaTipi
        CROSS JOIN geceler
    ),
    toplam_fiyatlar AS (
        SELECT oda_tipi_id, SUM(fiyat) AS toplam_fiyat
        FROM gecelik_fiyatlar
        GROUP BY oda_tipi_id
    )
    SELECT Oda.id AS oda_id,
           Oda.oda_numarasi,
           Oda.kat,
           OdaTipi.id AS oda_tipi_id,
           OdaTipi.tip_adi,
           OdaTipi.kapasite,
           DATEDIFF(aranan_cikis, aranan_giris) AS gece_sayisi,
           toplam_fiyatlar.toplam_fiyat
    FROM Oda
    JOIN OdaTipi ON OdaTipi.id = Oda.oda_tipi_id
    JOIN toplam_fiyatlar ON toplam_fiyatlar.oda_tipi_id = OdaTipi.id
    WHERE (aranan_tip_id IS NULL OR Oda.oda_tipi_id = aranan_tip_id)
      AND Oda.durum <> 'bakımda'
      AND NOT EXISTS (
          SELECT 1
          FROM Rezervasyon
          WHERE Rezervasyon.oda_id = Oda.id
            AND Rezervasyon.durum <> 'iptal'
            AND Rezervasyon.giris_tarihi < aranan_cikis
            AND Rezervasyon.cikis_tarihi > aranan_giris
      )
    ORDER BY OdaTipi.tip_adi, Oda.oda_numarasi;
END$$


-- 2) Bir konaklamanın toplam tutarını hesaplar: sezon fiyatları (her gece için) + ek hizmetler.
-- Geceler rezervasyonun giriş ve çıkış tarihlerine göre sayılır (çıkış günü gece sayılmaz).
-- Sonuçlar OUT parametreleriyle döner, böylece sp_checkout da bu prosedürü kullanabilir.
DROP PROCEDURE IF EXISTS sp_tutar_hesapla$$
CREATE PROCEDURE sp_tutar_hesapla(
    IN aranan_konaklama_id INT,
    OUT oda_ucreti DECIMAL(10, 2),
    OUT hizmet_ucreti DECIMAL(10, 2),
    OUT genel_toplam DECIMAL(10, 2)
)
BEGIN
    DECLARE konaklama_giris DATE DEFAULT NULL;
    DECLARE konaklama_cikis DATE DEFAULT NULL;
    DECLARE konaklama_tip_id INT DEFAULT NULL;
    DECLARE tip_temel_fiyat DECIMAL(10, 2) DEFAULT 0;

    SELECT Rezervasyon.giris_tarihi, Rezervasyon.cikis_tarihi, Oda.oda_tipi_id, OdaTipi.temel_fiyat
    INTO konaklama_giris, konaklama_cikis, konaklama_tip_id, tip_temel_fiyat
    FROM Konaklama
    JOIN Rezervasyon ON Rezervasyon.id = Konaklama.rezervasyon_id
    JOIN Oda ON Oda.id = Rezervasyon.oda_id
    JOIN OdaTipi ON OdaTipi.id = Oda.oda_tipi_id
    WHERE Konaklama.id = aranan_konaklama_id;

    IF konaklama_giris IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 45002,
            MESSAGE_TEXT = 'Konaklama kaydı bulunamadı.';
    END IF;

    -- Konaklanan her gece için o geceye ait sezon fiyatı toplanır
    WITH RECURSIVE geceler AS (
        SELECT konaklama_giris AS gece
        UNION ALL
        SELECT DATE_ADD(gece, INTERVAL 1 DAY)
        FROM geceler
        WHERE DATE_ADD(gece, INTERVAL 1 DAY) < konaklama_cikis
    ),
    gecelik_fiyatlar AS (
        SELECT COALESCE(
                   (SELECT SezonFiyati.gecelik_fiyat
                    FROM SezonFiyati
                    WHERE SezonFiyati.oda_tipi_id = konaklama_tip_id
                      AND geceler.gece BETWEEN SezonFiyati.baslangic_tarihi AND SezonFiyati.bitis_tarihi
                    ORDER BY SezonFiyati.baslangic_tarihi DESC, SezonFiyati.id DESC
                    LIMIT 1),
                   tip_temel_fiyat
               ) AS fiyat
        FROM geceler
    )
    SELECT COALESCE(SUM(fiyat), 0) INTO oda_ucreti
    FROM gecelik_fiyatlar;

    SELECT COALESCE(SUM(KonaklamaHizmeti.adet * KonaklamaHizmeti.birim_fiyat), 0) INTO hizmet_ucreti
    FROM KonaklamaHizmeti
    WHERE KonaklamaHizmeti.konaklama_id = aranan_konaklama_id;

    SET genel_toplam = oda_ucreti + hizmet_ucreti;
END$$


-- 3) Aylık doluluk oranı ve gelir raporu.
-- Doluluk = dolu oda-gecesi / (toplam oda sayısı x ayın gün sayısı)
-- Dolu sayılan rezervasyonlar: onaylı ve tamamlandı. Gelir: ayın içindeki ödemelerin toplamı.
-- İki sonuç kümesi döner: 1) genel özet, 2) oda tipi bazında doluluk.
DROP PROCEDURE IF EXISTS sp_aylik_rapor$$
CREATE PROCEDURE sp_aylik_rapor(
    IN rapor_yili INT,
    IN rapor_ayi INT
)
BEGIN
    DECLARE ay_baslangic DATE;
    DECLARE sonraki_ay_baslangic DATE;
    DECLARE ay_gun_sayisi INT;
    DECLARE toplam_oda_sayisi INT DEFAULT 0;
    DECLARE ay_dolu_gece INT DEFAULT 0;
    DECLARE aylik_gelir DECIMAL(12, 2) DEFAULT 0;

    IF rapor_yili IS NULL OR rapor_yili < 2000 OR rapor_yili > 2100
       OR rapor_ayi IS NULL OR rapor_ayi < 1 OR rapor_ayi > 12 THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 45002,
            MESSAGE_TEXT = 'Geçersiz yıl veya ay.';
    END IF;

    SET ay_baslangic = DATE(CONCAT(rapor_yili, '-', LPAD(rapor_ayi, 2, '0'), '-01'));
    SET sonraki_ay_baslangic = DATE_ADD(ay_baslangic, INTERVAL 1 MONTH);
    SET ay_gun_sayisi = DATEDIFF(sonraki_ay_baslangic, ay_baslangic);

    SELECT COUNT(*) INTO toplam_oda_sayisi FROM Oda;

    -- Rezervasyonun sadece o aya düşen geceleri sayılır
    SELECT COALESCE(SUM(GREATEST(0, DATEDIFF(
               LEAST(Rezervasyon.cikis_tarihi, sonraki_ay_baslangic),
               GREATEST(Rezervasyon.giris_tarihi, ay_baslangic)
           ))), 0)
    INTO ay_dolu_gece
    FROM Rezervasyon
    WHERE Rezervasyon.durum IN ('onaylı', 'tamamlandı')
      AND Rezervasyon.giris_tarihi < sonraki_ay_baslangic
      AND Rezervasyon.cikis_tarihi > ay_baslangic;

    SELECT COALESCE(SUM(Odeme.tutar), 0) INTO aylik_gelir
    FROM Odeme
    WHERE Odeme.tarih >= ay_baslangic
      AND Odeme.tarih < sonraki_ay_baslangic;

    -- Sonuç 1: genel özet
    SELECT rapor_yili AS yil,
           rapor_ayi AS ay,
           toplam_oda_sayisi AS oda_sayisi,
           ay_gun_sayisi AS gun_sayisi,
           ay_dolu_gece AS dolu_oda_gecesi,
           ROUND(ay_dolu_gece * 100 / NULLIF(toplam_oda_sayisi * ay_gun_sayisi, 0), 2) AS doluluk_orani,
           aylik_gelir AS gelir;

    -- Sonuç 2: oda tipi bazında doluluk
    SELECT tip_ozeti.tip_adi,
           tip_ozeti.oda_sayisi,
           tip_ozeti.dolu_oda_gecesi,
           ROUND(tip_ozeti.dolu_oda_gecesi * 100 / (tip_ozeti.oda_sayisi * ay_gun_sayisi), 2) AS doluluk_orani
    FROM (
        SELECT OdaTipi.tip_adi,
               COUNT(DISTINCT Oda.id) AS oda_sayisi,
               COALESCE(SUM(GREATEST(0, DATEDIFF(
                   LEAST(Rezervasyon.cikis_tarihi, sonraki_ay_baslangic),
                   GREATEST(Rezervasyon.giris_tarihi, ay_baslangic)
               ))), 0) AS dolu_oda_gecesi
        FROM OdaTipi
        JOIN Oda ON Oda.oda_tipi_id = OdaTipi.id
        LEFT JOIN Rezervasyon ON Rezervasyon.oda_id = Oda.id
             AND Rezervasyon.durum IN ('onaylı', 'tamamlandı')
             AND Rezervasyon.giris_tarihi < sonraki_ay_baslangic
             AND Rezervasyon.cikis_tarihi > ay_baslangic
        GROUP BY OdaTipi.id, OdaTipi.tip_adi
    ) AS tip_ozeti
    ORDER BY tip_ozeti.tip_adi;
END$$


-- 4) Check-out: tek transaction içinde
--    konaklama kapatılır -> (trigger oda durumunu 'temizlikte', rezervasyonu 'tamamlandı' yapar) -> ödeme kaydedilir.
-- Herhangi bir adım hata verirse tüm değişiklikler (trigger'ların yaptıkları dahil) geri alınır.
-- Ödeme tutarı = genel toplam - daha önce alınmış ödemeler (ön ödeme olabilir).
DROP PROCEDURE IF EXISTS sp_checkout$$
CREATE PROCEDURE sp_checkout(
    IN cikis_konaklama_id INT,
    IN cikis_personel_id INT,
    IN cikis_odeme_turu VARCHAR(10)
)
BEGIN
    DECLARE bulunan_konaklama_id INT DEFAULT NULL;
    DECLARE kapanis_zamani DATETIME DEFAULT NULL;
    DECLARE oda_ucreti DECIMAL(10, 2) DEFAULT 0;
    DECLARE hizmet_ucreti DECIMAL(10, 2) DEFAULT 0;
    DECLARE genel_toplam DECIMAL(10, 2) DEFAULT 0;
    DECLARE onceki_odemeler DECIMAL(10, 2) DEFAULT 0;
    DECLARE odenecek_tutar DECIMAL(10, 2) DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Aynı konaklamaya aynı anda iki check-out yapılmasın diye satır kilitlenir
    SELECT Konaklama.id, Konaklama.gercek_cikis_zamani
    INTO bulunan_konaklama_id, kapanis_zamani
    FROM Konaklama
    WHERE Konaklama.id = cikis_konaklama_id
    FOR UPDATE;

    IF bulunan_konaklama_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 45002,
            MESSAGE_TEXT = 'Konaklama kaydı bulunamadı.';
    END IF;

    IF kapanis_zamani IS NOT NULL THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 45001,
            MESSAGE_TEXT = 'Bu konaklama için check-out zaten yapılmış.';
    END IF;

    CALL sp_tutar_hesapla(cikis_konaklama_id, oda_ucreti, hizmet_ucreti, genel_toplam);

    SELECT COALESCE(SUM(Odeme.tutar), 0) INTO onceki_odemeler
    FROM Odeme
    WHERE Odeme.konaklama_id = cikis_konaklama_id;

    SET odenecek_tutar = GREATEST(genel_toplam - onceki_odemeler, 0);

    -- Adım 1: konaklamayı kapat (oda durumunu trigger günceller)
    UPDATE Konaklama
    SET gercek_cikis_zamani = NOW(),
        cikis_yapan_personel_id = cikis_personel_id,
        toplam_tutar = genel_toplam
    WHERE Konaklama.id = cikis_konaklama_id;

    -- Adım 2: ödemeyi kaydet. Burada hata olursa adım 1 ve trigger'ın değişiklikleri de geri alınır.
    IF cikis_odeme_turu IS NULL OR cikis_odeme_turu NOT IN ('nakit', 'kart') THEN
        SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 45002,
            MESSAGE_TEXT = 'Geçersiz ödeme türü (nakit veya kart olmalı).';
    END IF;

    IF odenecek_tutar > 0 THEN
        INSERT INTO Odeme (konaklama_id, tutar, odeme_turu)
        VALUES (cikis_konaklama_id, odenecek_tutar, cikis_odeme_turu);
    END IF;

    COMMIT;

    SELECT cikis_konaklama_id AS konaklama_id,
           oda_ucreti,
           hizmet_ucreti,
           genel_toplam,
           onceki_odemeler,
           odenecek_tutar AS tahsil_edilen,
           cikis_odeme_turu AS odeme_turu;
END$$

DELIMITER ;

-- Kontrol: SHOW PROCEDURE STATUS WHERE Db = 'Otel_DB';   -- 4 prosedür
