
-- Otel Yonetim Sistemi Veritabani
-- Veritabani ve Yonetim Sistemleri donem projesi
 --Otelin tüm verisinin (odalar, misafirler, rezervasyonlar, ödemeler vb.) düzenli şekilde saklanacağı “boş tabloları” kuran koddur.
CREATE DATABASE IF NOT EXISTS otel_db;
USE otel_db;
 
-- oda tipleri (standart, deluxe, suit)
CREATE TABLE OdaTipi (
    TipID INT AUTO_INCREMENT PRIMARY KEY,
    TipAdi ENUM('standart', 'deluxe', 'suit') NOT NULL,
    Kapasite INT NOT NULL,
    Aciklama TEXT,
    TemelFiyat DECIMAL(10,2) NOT NULL
);
 
-- odalar
CREATE TABLE Oda (
    OdaID INT AUTO_INCREMENT PRIMARY KEY,
    OdaNumarasi VARCHAR(10) NOT NULL UNIQUE,
    Kat INT NOT NULL,
    TipID INT NOT NULL,
    Durum ENUM('boş', 'dolu', 'temizlikte', 'bakımda') DEFAULT 'boş',
    FOREIGN KEY (TipID) REFERENCES OdaTipi(TipID)
);
 
-- sezona gore fiyatlar
CREATE TABLE SezonFiyati (
    SezonID INT AUTO_INCREMENT PRIMARY KEY,
    TipID INT NOT NULL,
    BaslangicTarihi DATE NOT NULL,
    BitisTarihi DATE NOT NULL,
    GecelikFiyat DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (TipID) REFERENCES OdaTipi(TipID)
);
 
-- misafirler
CREATE TABLE Misafir (
    MisafirID INT AUTO_INCREMENT PRIMARY KEY,
    Ad VARCHAR(50) NOT NULL,
    Soyad VARCHAR(50) NOT NULL,
    TcPasaportNo VARCHAR(20) NOT NULL UNIQUE,
    Telefon VARCHAR(20),
    Eposta VARCHAR(100) NOT NULL UNIQUE,
    DogumTarihi DATE
);
 
-- personeller
CREATE TABLE Personel (
    PersonelID INT AUTO_INCREMENT PRIMARY KEY,
    Ad VARCHAR(50) NOT NULL,
    Soyad VARCHAR(50) NOT NULL,
    Gorev ENUM('resepsiyon', 'kat görevlisi', 'yönetici') NOT NULL,
    IseGirisTarihi DATE NOT NULL
);
 
-- sisteme giris yapan kullanicilar
-- misafir ise MisafirID dolu, personel ise PersonelID dolu olacak
CREATE TABLE Kullanici (
    KullaniciID INT AUTO_INCREMENT PRIMARY KEY,
    Eposta VARCHAR(100) NOT NULL UNIQUE,
    SifreHash VARCHAR(255) NOT NULL,
    Rol ENUM('misafir', 'resepsiyon', 'yönetici') NOT NULL,
    MisafirID INT UNIQUE,
    PersonelID INT UNIQUE,
    FOREIGN KEY (MisafirID) REFERENCES Misafir(MisafirID) ON DELETE CASCADE,
    FOREIGN KEY (PersonelID) REFERENCES Personel(PersonelID) ON DELETE CASCADE
);
 
-- rezervasyonlar
CREATE TABLE Rezervasyon (
    RezervasyonID INT AUTO_INCREMENT PRIMARY KEY,
    MisafirID INT NOT NULL,
    OdaID INT NOT NULL,
    GirisTarihi DATE NOT NULL,
    CikisTarihi DATE NOT NULL,
    KisiSayisi INT NOT NULL,
    Durum ENUM('beklemede', 'onaylı', 'iptal', 'tamamlandı') DEFAULT 'beklemede',
    OlusturmaTarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (MisafirID) REFERENCES Misafir(MisafirID),
    FOREIGN KEY (OdaID) REFERENCES Oda(OdaID)
);
 
-- misafir otele gelince olusan konaklama kaydi
CREATE TABLE Konaklama (
    KonaklamaID INT AUTO_INCREMENT PRIMARY KEY,
    RezervasyonID INT NOT NULL UNIQUE,
    GercekGirisZamani DATETIME NOT NULL,
    GercekCikisZamani DATETIME,
    IslemiYapanPersonelID INT NOT NULL,
    FOREIGN KEY (RezervasyonID) REFERENCES Rezervasyon(RezervasyonID),
    FOREIGN KEY (IslemiYapanPersonelID) REFERENCES Personel(PersonelID)
);
 
-- ek hizmetler (kahvalti, minibar vs.)
CREATE TABLE EkHizmet (
    HizmetID INT AUTO_INCREMENT PRIMARY KEY,
    HizmetAdi VARCHAR(100) NOT NULL,
    BirimFiyat DECIMAL(10,2) NOT NULL
);
 
-- konaklama sirasinda alinan hizmetler
CREATE TABLE KonaklamaHizmeti (
    KonaklamaHizmetID INT AUTO_INCREMENT PRIMARY KEY,
    KonaklamaID INT NOT NULL,
    HizmetID INT NOT NULL,
    Adet INT DEFAULT 1,
    Tarih DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (KonaklamaID) REFERENCES Konaklama(KonaklamaID),
    FOREIGN KEY (HizmetID) REFERENCES EkHizmet(HizmetID)
);
 
-- odemeler
CREATE TABLE Odeme (
    OdemeID INT AUTO_INCREMENT PRIMARY KEY,
    KonaklamaID INT NOT NULL,
    Tutar DECIMAL(10,2) NOT NULL,
    OdemeTuru ENUM('nakit', 'kart') NOT NULL,
    Tarih DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (KonaklamaID) REFERENCES Konaklama(KonaklamaID)
);
 
-- oda temizlik kayitlari
CREATE TABLE TemizlikKaydi (
    TemizlikID INT AUTO_INCREMENT PRIMARY KEY,
    OdaID INT NOT NULL,
    PersonelID INT NOT NULL,
    Tarih DATETIME DEFAULT CURRENT_TIMESTAMP,
    Durum ENUM('planlandı', 'tamamlandı') DEFAULT 'planlandı',
    FOREIGN KEY (OdaID) REFERENCES Oda(OdaID),
    FOREIGN KEY (PersonelID) REFERENCES Personel(PersonelID)
);
 
-- yapilan islemlerin logu (trigger ile doldurulacak)
CREATE TABLE IslemLog (
    LogID INT AUTO_INCREMENT PRIMARY KEY,
    TabloAdi VARCHAR(50) NOT NULL,
    IslemTipi ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    EskiVeri JSON,
    YeniVeri JSON,
    IslemZamani TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);