class Oda:
    def __init__(self, id, oda_numarasi, kat, oda_tipi_id, durum="boş", tip_adi=None, temel_fiyat=None):
        self.id = id
        self.oda_numarasi = oda_numarasi
        self.kat = kat
        self.oda_tipi_id = oda_tipi_id
        self.durum = durum
        self.tip_adi = tip_adi
        self.temel_fiyat = float(temel_fiyat) if temel_fiyat is not None else None

    def to_dict(self):
        veri = {
            "id": self.id,
            "oda_numarasi": self.oda_numarasi,
            "kat": self.kat,
            "oda_tipi_id": self.oda_tipi_id,
            "durum": self.durum
        }
        if self.tip_adi is not None:
            veri["tip_adi"] = self.tip_adi
        if self.temel_fiyat is not None:
            veri["temel_fiyat"] = self.temel_fiyat
        return veri