USE Otel_DB;
 
DELIMITER $$

DROP TRIGGER IF EXISTS trg_rezervasyon_cakisma_bi$$
CREATE TRIGGER trg_rezervasyon_cakisma_bi
BEFORE INSERT ON Rezervasyon
FOR EACH ROW
BEGIN
    DECLARE oda_kapasitesi INT DEFAULT NULL;
    DECLARE cakisan_sayisi INT DEFAULT 0;
    DECLARE hata_mesaji VARCHAR(200);
 
    IF NEW.durum <> 'iptal' THEN
        SELECT OdaTipi.kapasite INTO oda_kapasitesi FROM Oda JOIN OdaTipi ON OdaTipi.id = Oda.oda_tipi_id WHERE Oda.id = NEW.oda_id;
 
        IF oda_kapasitesi IS NOT NULL AND (NEW.kisi_sayisi < 1 OR NEW.kisi_sayisi > oda_kapasitesi) THEN
            SET hata_mesaji = CONCAT('Kişi sayısı geçersiz. Bu oda tipinin kapasitesi: ', oda_kapasitesi);
            SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 45002, MESSAGE_TEXT = hata_mesaji;
        END IF;

        SELECT COUNT(*) INTO cakisan_sayisi FROM Rezervasyon WHERE oda_id = NEW.oda_id
          AND durum <> 'iptal'
          AND giris_tarihi < NEW.cikis_tarihi
          AND cikis_tarihi > NEW.giris_tarihi
        FOR UPDATE;
 
        IF cakisan_sayisi > 0 THEN
            SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 45001,
                MESSAGE_TEXT = 'Oda seçilen tarihlerde dolu (çakışan rezervasyon var).';
        END IF;
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_rezervasyon_cakisma_bu$$
CREATE TRIGGER trg_rezervasyon_cakisma_bu
BEFORE UPDATE ON Rezervasyon
FOR EACH ROW
BEGIN
    DECLARE oda_kapasitesi INT DEFAULT NULL;
    DECLARE cakisan_sayisi INT DEFAULT 0;
    DECLARE hata_mesaji VARCHAR(200);
 
    IF NEW.durum <> 'iptal' THEN
        SELECT OdaTipi.kapasite INTO oda_kapasitesi FROM Oda JOIN OdaTipi ON OdaTipi.id = Oda.oda_tipi_id WHERE Oda.id = NEW.oda_id;
 
        IF oda_kapasitesi IS NOT NULL AND (NEW.kisi_sayisi < 1 OR NEW.kisi_sayisi > oda_kapasitesi) THEN
            SET hata_mesaji = CONCAT('Kişi sayısı geçersiz. Bu oda tipinin kapasitesi: ', oda_kapasitesi);
            SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 45002, MESSAGE_TEXT = hata_mesaji;
        END IF;

        SELECT COUNT(*) INTO cakisan_sayisi
        FROM Rezervasyon
        WHERE oda_id = NEW.oda_id
          AND durum <> 'iptal'
          AND id <> NEW.id
          AND giris_tarihi < NEW.cikis_tarihi
          AND cikis_tarihi > NEW.giris_tarihi
        FOR UPDATE;
 
        IF cakisan_sayisi > 0 THEN
            SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 45001,
                MESSAGE_TEXT = 'Oda seçilen tarihlerde dolu (çakışan rezervasyon var).';
        END IF;
    END IF;
END$$
 

DROP TRIGGER IF EXISTS trg_konaklama_checkin_kontrol_bi$$
CREATE TRIGGER trg_konaklama_checkin_kontrol_bi
BEFORE INSERT ON Konaklama
FOR EACH ROW
BEGIN
    DECLARE rez_durumu VARCHAR(20);
    DECLARE rez_oda_id INT;
    DECLARE oda_durumu VARCHAR(20);
 
    IF NEW.gercek_cikis_zamani IS NULL THEN
        SELECT durum, oda_id INTO rez_durumu, rez_oda_id FROM Rezervasyon WHERE id = NEW.rezervasyon_id;
 
        IF rez_durumu IS NULL OR rez_durumu <> 'onaylı' THEN
            SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 45002,
                MESSAGE_TEXT = 'Check-in yapılamaz: rezervasyon onaylı durumda değil.';
        END IF;
 
        SELECT durum INTO oda_durumu
        FROM Oda
        WHERE id = rez_oda_id;
 
        IF oda_durumu <> 'boş' THEN
            SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 45001,
                MESSAGE_TEXT = 'Check-in yapılamaz: oda şu anda boş değil.';
        END IF;
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_konaklama_checkin_ai$$
CREATE TRIGGER trg_konaklama_checkin_ai
AFTER INSERT ON Konaklama
FOR EACH ROW
BEGIN
    IF NEW.gercek_cikis_zamani IS NULL THEN
        UPDATE Oda
        SET durum = 'dolu'
        WHERE id = (SELECT oda_id FROM Rezervasyon WHERE id = NEW.rezervasyon_id);
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_konaklama_checkout_au$$
CREATE TRIGGER trg_konaklama_checkout_au
AFTER UPDATE ON Konaklama
FOR EACH ROW
BEGIN
    IF OLD.gercek_cikis_zamani IS NULL AND NEW.gercek_cikis_zamani IS NOT NULL THEN
        UPDATE Oda
        SET durum = 'temizlikte'
        WHERE id = (SELECT oda_id FROM Rezervasyon WHERE id = NEW.rezervasyon_id);
 
        UPDATE Rezervasyon
        SET durum = 'tamamlandı'
        WHERE id = NEW.rezervasyon_id;
    END IF;
END$$

 
DROP TRIGGER IF EXISTS trg_log_rezervasyon_ai$$
CREATE TRIGGER trg_log_rezervasyon_ai
AFTER INSERT ON Rezervasyon
FOR EACH ROW
BEGIN
    INSERT INTO IslemLog (tablo_adi, islem_turu, kayit_id, eski_deger, yeni_deger, kullanici)
    VALUES ('Rezervasyon', 'INSERT', NEW.id, NULL,
            JSON_OBJECT('misafir_id', NEW.misafir_id, 'oda_id', NEW.oda_id,'giris_tarihi', NEW.giris_tarihi, 'cikis_tarihi', NEW.cikis_tarihi,'kisi_sayisi', NEW.kisi_sayisi, 'durum', NEW.durum),
            LEFT(COALESCE(@app_user, 'SISTEM'), 50));
END$$
 
DROP TRIGGER IF EXISTS trg_log_rezervasyon_au$$
CREATE TRIGGER trg_log_rezervasyon_au
AFTER UPDATE ON Rezervasyon
FOR EACH ROW
BEGIN
    INSERT INTO IslemLog (tablo_adi, islem_turu, kayit_id, eski_deger, yeni_deger, kullanici)
    VALUES ('Rezervasyon', 'UPDATE', NEW.id,
            JSON_OBJECT('misafir_id', OLD.misafir_id, 'oda_id', OLD.oda_id,'giris_tarihi', OLD.giris_tarihi, 'cikis_tarihi', OLD.cikis_tarihi,'kisi_sayisi', OLD.kisi_sayisi, 'durum', OLD.durum),
            JSON_OBJECT('misafir_id', NEW.misafir_id, 'oda_id', NEW.oda_id,'giris_tarihi', NEW.giris_tarihi, 'cikis_tarihi', NEW.cikis_tarihi,'kisi_sayisi', NEW.kisi_sayisi, 'durum', NEW.durum),
            LEFT(COALESCE(@app_user, 'SISTEM'), 50));
END$$
 
DROP TRIGGER IF EXISTS trg_log_rezervasyon_ad$$
CREATE TRIGGER trg_log_rezervasyon_ad
AFTER DELETE ON Rezervasyon
FOR EACH ROW
BEGIN
    INSERT INTO IslemLog (tablo_adi, islem_turu, kayit_id, eski_deger, yeni_deger, kullanici)
    VALUES ('Rezervasyon', 'DELETE', OLD.id,
            JSON_OBJECT('misafir_id', OLD.misafir_id, 'oda_id', OLD.oda_id,'giris_tarihi', OLD.giris_tarihi, 'cikis_tarihi', OLD.cikis_tarihi,'kisi_sayisi', OLD.kisi_sayisi, 'durum', OLD.durum),
            NULL,
            LEFT(COALESCE(@app_user, 'SISTEM'), 50));
END$$
 
DROP TRIGGER IF EXISTS trg_log_odeme_ai$$
CREATE TRIGGER trg_log_odeme_ai
AFTER INSERT ON Odeme
FOR EACH ROW
BEGIN
    INSERT INTO IslemLog (tablo_adi, islem_turu, kayit_id, eski_deger, yeni_deger, kullanici)
    VALUES ('Odeme', 'INSERT', NEW.id, NULL,
            JSON_OBJECT('konaklama_id', NEW.konaklama_id, 'tutar', NEW.tutar, 'odeme_turu', NEW.odeme_turu),
            LEFT(COALESCE(@app_user, 'SISTEM'), 50));
END$$
 
DROP TRIGGER IF EXISTS trg_log_odeme_au$$
CREATE TRIGGER trg_log_odeme_au
AFTER UPDATE ON Odeme
FOR EACH ROW
BEGIN
    INSERT INTO IslemLog (tablo_adi, islem_turu, kayit_id, eski_deger, yeni_deger, kullanici)
    VALUES ('Odeme', 'UPDATE', NEW.id,
            JSON_OBJECT('konaklama_id', OLD.konaklama_id, 'tutar', OLD.tutar,'odeme_turu', OLD.odeme_turu),
            JSON_OBJECT('konaklama_id', NEW.konaklama_id, 'tutar', NEW.tutar,'odeme_turu', NEW.odeme_turu),
            LEFT(COALESCE(@app_user, 'SISTEM'), 50));
END$$
 
DROP TRIGGER IF EXISTS trg_log_odeme_ad$$
CREATE TRIGGER trg_log_odeme_ad
AFTER DELETE ON Odeme
FOR EACH ROW
BEGIN
    INSERT INTO IslemLog (tablo_adi, islem_turu, kayit_id, eski_deger, yeni_deger, kullanici)
    VALUES ('Odeme', 'DELETE', OLD.id,
            JSON_OBJECT('konaklama_id', OLD.konaklama_id, 'tutar', OLD.tutar, 'odeme_turu', OLD.odeme_turu),
            NULL,
            LEFT(COALESCE(@app_user, 'SISTEM'), 50));
END$$
 
DELIMITER ;
 