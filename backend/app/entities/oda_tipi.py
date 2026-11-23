class OdaTipi:
    def __init__(self, id, ad, aciklama, kapasite, taban_fiyat):
        self.id = id
        self.ad = ad
        self.aciklama = aciklama
        self.kapasite = kapasite
        self.taban_fiyat = taban_fiyat

    def to_dict(self):
        """OdaTipi nesnesini JSON formatına çevrilebilmesi için sözlüğe (dictionary) dönüştürür."""
        return {
            "id": self.id,
            "ad": self.ad,
            "aciklama": self.aciklama,
            "kapasite": self.kapasite,
            "taban_fiyat": float(self.taban_fiyat) if self.taban_fiyat else 0.0
        }