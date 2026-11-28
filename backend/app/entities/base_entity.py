from datetime import date, datetime, time, timedelta
from decimal import Decimal


def json_uyumlu(deger):
    if isinstance(deger, (datetime, date, time)):
        return deger.isoformat()
    if isinstance(deger, Decimal):
        return float(deger)
    if isinstance(deger, timedelta):
        return str(deger)
    if isinstance(deger, Entity):
        return deger.to_dict()
    if isinstance(deger, (list, tuple, set)):
        return [json_uyumlu(d) for d in deger]
    if isinstance(deger, dict):
        return {k: json_uyumlu(v) for k, v in deger.items()}
    return deger


class Entity:

    ALANLAR = ()
    GIZLI = ()
    OPSIYONEL = ()
    VARSAYILAN = {}

    def __init__(self, *args, **veri):
        if len(args) > len(self.ALANLAR):
            raise TypeError(
                f"{type(self).__name__} en fazla {len(self.ALANLAR)} pozisyonel argüman alır, "
                f"{len(args)} verildi"
            )
        for alan, deger in zip(self.ALANLAR, args):
            if alan in veri:
                raise TypeError(f"{type(self).__name__}: '{alan}' birden fazla kez verildi")
            veri[alan] = deger

        for alan in self.ALANLAR:
            deger = veri.get(alan)
            if deger is None:
                deger = self.VARSAYILAN.get(alan)
            setattr(self, alan, deger)

    @classmethod
    def from_satir(cls, satir):
        """Sözlük (DB satırı) -> nesne. Satır yoksa None döner."""
        return cls(**satir) if satir else None

    @classmethod
    def liste(cls, satirlar):
        """Satır listesi -> nesne listesi."""
        return [cls(**s) for s in (satirlar or [])]

    def to_dict(self):
        sonuc = {}
        for alan in self.ALANLAR:
            if alan in self.GIZLI:
                continue
            deger = getattr(self, alan)
            if deger is None and alan in self.OPSIYONEL:
                continue
            sonuc[alan] = json_uyumlu(deger)
        return sonuc

    def __repr__(self):
        alanlar = ", ".join( f"{a}={getattr(self, a)!r}" for a in self.ALANLAR if a not in self.GIZLI)
        return f"{type(self).__name__}({alanlar})"
