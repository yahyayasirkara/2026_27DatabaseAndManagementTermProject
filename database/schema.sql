CREATE DATABASE IF NOT EXISTS Otel_DB
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE Otel_DB;

DROP TABLE IF EXISTS OdaTipi;
CREATE TABLE OdaTipi (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tip_adi VARCHAR(50) NOT NULL UNIQUE,
    kapasite INT NOT NULL,
    aciklama TEXT,
    temel_fiyat DECIMAL(10, 2) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE Oda (
    id INT AUTO_INCREMENT PRIMARY KEY,
    oda_numarasi VARCHAR(10) NOT NULL UNIQUE,
    kat INT NOT NULL,
    oda_tipi_id INT NOT NULL,
    durum ENUM('boş', 'dolu', 'temizlikte', 'bakımda') NOT NULL DEFAULT 'boş',
    CONSTRAINT fk_oda_tipi FOREIGN KEY (oda_tipi_id) REFERENCES OdaTipi(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE SezonFiyati (
    id INT AUTO_INCREMENT PRIMARY KEY,
    oda_tipi_id INT NOT NULL,
    baslangic_tarihi DATE NOT NULL,
    bitis_tarihi DATE NOT NULL,
    gecelik_fiyat DECIMAL(10, 2) NOT NULL,
    CONSTRAINT fk_sezon_oda_tipi FOREIGN KEY (oda_tipi_id) REFERENCES OdaTipi(id) ON DELETE CASCADE,
    CONSTRAINT chk_sezon_tarih CHECK (bitis_tarihi >= baslangic_tarihi)
) ENGINE=InnoDB;

CREATE TABLE Misafir (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ad VARCHAR(50) NOT NULL,
    soyad VARCHAR(50) NOT NULL,
    tc_pasaport_no VARCHAR(20) NOT NULL UNIQUE,
    telefon VARCHAR(20) NOT NULL,
    eposta VARCHAR(100) NOT NULL UNIQUE,
    dogum_tarihi DATE NOT NULL
) ENGINE=InnoDB;

CREATE TABLE Personel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ad VARCHAR(50) NOT NULL,
    soyad VARCHAR(50) NOT NULL,
    gorev ENUM('resepsiyon', 'kat görevlisi', 'yönetici') NOT NULL,
    ise_giris_tarihi DATE NOT NULL
) ENGINE=InnoDB;

CREATE TABLE Kullanici (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kullanici_adi VARCHAR(50) NOT NULL UNIQUE,
    sifre_hash VARCHAR(255) NOT NULL,
    rol ENUM('misafir', 'resepsiyon', 'yönetici') NOT NULL,
    misafir_id INT NULL UNIQUE,
    personel_id INT NULL UNIQUE,
    CONSTRAINT fk_kullanici_misafir FOREIGN KEY (misafir_id) REFERENCES Misafir(id) ON DELETE CASCADE,
    CONSTRAINT fk_kullanici_personel FOREIGN KEY (personel_id) REFERENCES Personel(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Rezervasyon (
    id INT AUTO_INCREMENT PRIMARY KEY,
    misafir_id INT NOT NULL,
    oda_id INT NOT NULL,
    giris_tarihi DATE NOT NULL,
    cikis_tarihi DATE NOT NULL,
    kisi_sayisi INT NOT NULL,
    durum ENUM('beklemede', 'onaylı', 'iptal', 'tamamlandı') NOT NULL DEFAULT 'beklemede',
    olusturma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rezervasyon_misafir FOREIGN KEY (misafir_id) REFERENCES Misafir(id) ON DELETE RESTRICT,
    CONSTRAINT fk_rezervasyon_oda FOREIGN KEY (oda_id) REFERENCES Oda(id) ON DELETE RESTRICT,
    CONSTRAINT chk_rezervasyon_tarih CHECK (cikis_tarihi > giris_tarihi)
) ENGINE=InnoDB;

CREATE TABLE Konaklama (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rezervasyon_id INT NOT NULL UNIQUE,
    gercek_giris_zamani DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    gercek_cikis_zamani DATETIME NULL,
    giris_yapan_personel_id INT NOT NULL,
    cikis_yapan_personel_id INT NULL,
    toplam_tutar DECIMAL(10, 2) DEFAULT 0.00,
    CONSTRAINT fk_konaklama_rezervasyon FOREIGN KEY (rezervasyon_id) REFERENCES Rezervasyon(id) ON DELETE RESTRICT,
    CONSTRAINT fk_konaklama_giris_personel FOREIGN KEY (giris_yapan_personel_id) REFERENCES Personel(id) ON DELETE RESTRICT,
    CONSTRAINT fk_konaklama_cikis_personel FOREIGN KEY (cikis_yapan_personel_id) REFERENCES Personel(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE EkHizmet (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hizmet_adi VARCHAR(100) NOT NULL UNIQUE,
    birim_fiyat DECIMAL(10, 2) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE KonaklamaHizmeti (
    id INT AUTO_INCREMENT PRIMARY KEY,
    konaklama_id INT NOT NULL,
    ek_hizmet_id INT NOT NULL,
    adet INT NOT NULL DEFAULT 1,
    birim_fiyat DECIMAL(10, 2) NOT NULL,
    tarih DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_kh_konaklama FOREIGN KEY (konaklama_id) REFERENCES Konaklama(id) ON DELETE CASCADE,
    CONSTRAINT fk_kh_ek_hizmet FOREIGN KEY (ek_hizmet_id) REFERENCES EkHizmet(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE Odeme (
    id INT AUTO_INCREMENT PRIMARY KEY,
    konaklama_id INT NOT NULL,
    tutar DECIMAL(10, 2) NOT NULL,
    odeme_turu ENUM('nakit', 'kart') NOT NULL,
    tarih DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_odeme_konaklama FOREIGN KEY (konaklama_id) REFERENCES Konaklama(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE TemizlikKaydi (
    id INT AUTO_INCREMENT PRIMARY KEY,
    oda_id INT NOT NULL,
    personel_id INT NOT NULL,
    tarih DATETIME DEFAULT CURRENT_TIMESTAMP,
    durum ENUM('temizlendi', 'kontrol_bekliyor', 'onaylandı') NOT NULL DEFAULT 'temizlendi',
    CONSTRAINT fk_temizlik_oda FOREIGN KEY (oda_id) REFERENCES Oda(id) ON DELETE CASCADE,
    CONSTRAINT fk_temizlik_personel FOREIGN KEY (personel_id) REFERENCES Personel(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IslemLog (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tablo_adi VARCHAR(50) NOT NULL,
    islem_turu ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    kayit_id INT NOT NULL,
    eski_deger JSON NULL,
    yeni_deger JSON NULL,
    islem_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
    kullanici VARCHAR(50) DEFAULT 'SISTEM'
) ENGINE=InnoDB;

CREATE INDEX idx_rezervasyon_tarihler ON Rezervasyon (giris_tarihi, cikis_tarihi);
CREATE INDEX idx_misafir_eposta ON Misafir (eposta);
CREATE INDEX idx_oda_numarasi ON Oda (oda_numarasi);