class Rezervasyon:
    def __init__(
        self,
        id,
        misafir_id,
        oda_id,
        giris_tarihi,
        cikis_tarihi,
        kisi_sayisi,
        durum="beklemede",
        olusturma_tarihi=None,
        misafir_ad_soyad=None,
        oda_numarasi=None
    ):
        self.id = id
        self.misafir_id = misafir_id
        self.oda_id = oda_id
        self.giris_tarihi = giris_tarihi.isoformat() if hasattr(giris_tarihi, "isoformat") else giris_tarihi
        self.cikis_tarihi = cikis_tarihi.isoformat() if hasattr(cikis_tarihi, "isoformat") else cikis_tarihi
        self.kisi_sayisi = kisi_sayisi
        self.durum = durum
        self.olusturma_tarihi = (
            olusturma_tarihi.isoformat() if hasattr(olusturma_tarihi, "isoformat") else olusturma_tarihi
        )
        self.misafir_ad_soyad = misafir_ad_soyad
        self.oda_numarasi = oda_numarasi

    def to_dict(self):
        veri = {
            "id": self.id,
            "misafir_id": self.misafir_id,
            "oda_id": self.oda_id,
            "giris_tarihi": self.giris_tarihi,
            "cikis_tarihi": self.cikis_tarihi,
            "kisi_sayisi": self.kisi_sayisi,
            "durum": self.durum,
            "olusturma_tarihi": self.olusturma_tarihi
        }
        if self.misafir_ad_soyad is not None:
            veri["misafir_ad_soyad"] = self.misafir_ad_soyad
        if self.oda_numarasi is not None:
            veri["oda_numarasi"] = self.oda_numarasi
        return veri