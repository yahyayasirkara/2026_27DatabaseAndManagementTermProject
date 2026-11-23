from datetime import date

class Misafir:
    def __init__(self, id, ad, soyad, tc_pasaport_no, telefon, eposta, dogum_tarihi):
        self.id = id
        self.ad = ad
        self.soyad = soyad
        self.tc_pasaport_no = tc_pasaport_no
        self.telefon = telefon
        self.eposta = eposta
        self.dogum_tarihi = dogum_tarihi

    def to_dict(self):
        return {
            "id": self.id,
            "ad": self.ad,
            "soyad": self.soyad,
            "tc_pasaport_no": self.tc_pasaport_no,
            "telefon": self.telefon,
            "eposta": self.eposta,
            "dogum_tarihi": self.dogum_tarihi.isoformat() if isinstance(self.dogum_tarihi, date) else str(self.dogum_tarihi)
        }