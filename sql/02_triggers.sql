

--Otel kurallarının (aynı odaya çifte rezervasyon olmasın, oda durumu otomatik değişsin,
--önemli işlemler kayda alınsın) Flask koduna güvenmeden doğrudan veritabanı tarafından uygulanmasını sağlar.



USE otel_db;
 
DELIMITER //
 
-- 1. ayni odaya cakisan tarihte rezervasyon yapilmasin
-- rezervasyon eklenmeden once calisir, tarihler cakisiyorsa hata verir
CREATE TRIGGER trg_rezervasyon_cakisma_kontrol
BEFORE INSERT ON Rezervasyon
FOR EACH ROW
BEGIN
    DECLARE sayi INT;
 
    SELECT COUNT(*) INTO sayi
    FROM Rezervasyon
    WHERE OdaID = NEW.OdaID
      AND Durum IN ('beklemede', 'onaylı')
      AND NEW.GirisTarihi < CikisTarihi
      AND NEW.CikisTarihi > GirisTarihi;
 
    IF sayi > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Bu oda bu tarihlerde dolu!';
    END IF;
END //
 
-- 2a. check-in olunca oda durumu dolu olsun
-- konaklama tablosuna kayit eklenince calisir
CREATE TRIGGER trg_checkin_oda_durumu
AFTER INSERT ON Konaklama
FOR EACH ROW
BEGIN
    UPDATE Oda
    SET Durum = 'dolu'
    WHERE OdaID = (SELECT OdaID FROM Rezervasyon WHERE RezervasyonID = NEW.RezervasyonID);
END //
 
-- 2b. check-out olunca oda temizlikte olsun
-- cikis zamani ilk kez doldurulunca calisir
CREATE TRIGGER trg_checkout_oda_durumu
AFTER UPDATE ON Konaklama
FOR EACH ROW
BEGIN
    IF NEW.GercekCikisZamani IS NOT NULL AND OLD.GercekCikisZamani IS NULL THEN
        UPDATE Oda
        SET Durum = 'temizlikte'
        WHERE OdaID = (SELECT OdaID FROM Rezervasyon WHERE RezervasyonID = NEW.RezervasyonID);
    END IF;
END //
 
-- 3a. rezervasyon guncellenince IslemLog'a yaz
-- eski ve yeni durumu kaydediyoruz
CREATE TRIGGER trg_rezervasyon_log
AFTER UPDATE ON Rezervasyon
FOR EACH ROW
BEGIN
    INSERT INTO IslemLog (TabloAdi, IslemTipi, EskiVeri, YeniVeri)
    VALUES ('Rezervasyon', 'UPDATE',
            JSON_OBJECT('RezervasyonID', OLD.RezervasyonID, 'Durum', OLD.Durum),
            JSON_OBJECT('RezervasyonID', NEW.RezervasyonID, 'Durum', NEW.Durum));
END //
 
-- 3b. odeme eklenince IslemLog'a yaz
CREATE TRIGGER trg_odeme_log
AFTER INSERT ON Odeme
FOR EACH ROW
BEGIN
    INSERT INTO IslemLog (TabloAdi, IslemTipi, YeniVeri)
    VALUES ('Odeme', 'INSERT',
            JSON_OBJECT('OdemeID', NEW.OdemeID, 'KonaklamaID', NEW.KonaklamaID, 'Tutar', NEW.Tutar));
END //
 
DELIMITER ;