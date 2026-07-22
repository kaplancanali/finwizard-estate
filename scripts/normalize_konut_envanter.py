#!/usr/bin/env python3
"""Normalize KonutEnvanter checklist into frontend inventory.json.

Source CSV is often cp1254 with corrupted glyphs; we emit curated Turkish labels
aligned to the checklist structure (residential + commercial sections).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "frontend" / "src" / "lib" / "analysis" / "inventory.json"


def slug(text: str) -> str:
    table = str.maketrans(
        {
            "ç": "c",
            "ğ": "g",
            "ı": "i",
            "ö": "o",
            "ş": "s",
            "ü": "u",
            "Ç": "c",
            "Ğ": "g",
            "İ": "i",
            "Ö": "o",
            "Ş": "s",
            "Ü": "u",
        }
    )
    s = text.translate(table).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80] or "item"


INVENTORY = {
    "version": 1,
    "source": "KonutEnvanter.csv",
    "categories": [
        {
            "id": "location_region",
            "title": "Konum ve Bölge Analizi",
            "commercial": False,
            "items": [
                "Ulaşım akslarına yakınlık",
                "İş merkezlerine erişim",
                "Sağlık hizmetine ulaşım",
                "Eğitim kurumlarına ulaşım",
                "Restoran çeşitliliği",
                "Kafe ve eğlence mekanlarına yakınlık",
                "AVM yakınlığı",
                "Hastaneye yakınlık",
                "Üniversitelere yakınlık",
                "Mahallenin gelir seviyesi",
                "Suç oranları ve güvenlik algısı",
                "Gürültü seviyesi",
                "Hava kalitesi",
                "Bölgedeki projeler",
                "Boş daire oranı",
                "Demografik yapı",
                "Okul kalitesi",
                "Gelecek 10 yıl potansiyeli",
                "Belediye yatırımları",
                "İmar değişiklik riski",
                "Otopark problemi",
                "Sel ve su baskını durumu",
                "Mahalle itibarı",
                "Yakın çevre emlak fiyat trendi",
            ],
        },
        {
            "id": "macro_appreciation",
            "title": "Makro Ekonomi ve Bölge Değer Artışı",
            "commercial": False,
            "items": [
                "Bölge nüfus artış oranı",
                "İç / dış göç durumları",
                "Konut art talep durumu",
                "Turizm etkisi",
                "Sanayi etkisi",
                "Hizmet sektörü etkisi",
                "Kamu istihdam etkisi",
                "Yaş ortalaması",
                "Yeni istihdam potansiyeli",
                "Mevcut istihdam durumu",
                "Fiyat artışları ile enflasyon ilişkisi",
                "Fiyat balonu durumu",
                "Bölge karşılaştırması",
                "Kentsel dönüşüm",
                "Kentsel dönüşüm etkisi",
            ],
        },
        {
            "id": "seismic_building",
            "title": "Deprem, Zemin ve Yapı Kalitesi",
            "commercial": False,
            "items": [
                "Bina yaşı",
                "Dönemin deprem yönetmeliğiyle kıyas",
                "Güncel deprem yönetmeliğiyle kıyas",
                "Zemin türü",
                "Dolgu alan riski",
                "Zeminin sıvılaşma riski",
                "Bina taşıyıcı sistem tipi",
                "Kolon kiriş düzeni",
                "Rutubet ve nem durumu",
                "Otopark durumu",
                "Otopark kolon dağılımı",
                "Kaçak tadilat veya ekleme durumu",
                "Asansör ve ortak alan durumu",
                "Bina bakım geçmişi",
                "Çatı durumu",
                "Su tesisatı",
                "Elektrik altyapısı",
                "Yangın güvenliği",
                "Daire planlama",
                "Bina oturma durumu",
                "Güneş alma durumu",
                "Havalandırma ve hava akışı",
                "Ses yalıtımı",
                "Binayı yapan şirket / Z raporu",
                "Profesyonel ekspertiz raporu",
            ],
        },
        {
            "id": "title_legal",
            "title": "Tapu, Hukuk ve Resmi Kontroller",
            "commercial": False,
            "items": [
                "Tapu türü",
                "Hisseli yapı (özel durum)",
                "İpotek durumu",
                "Projeye uygun yapı durumu",
                "İskan",
                "Ortak alan işgal durumu",
                "Satıcı mülkiyet yetkisi",
                "Aidat",
                "Aidat borç durumu",
                "Belediyeye borç durumu",
                "Site yönetimi dava durumu",
                "Tahliye riski",
                "Kat planı ve durumu",
                "Metrekare doğruluğu",
                "Dava ve ihtilaf durumu",
                "Resmi ekspertiz değerlendirmesi",
            ],
        },
        {
            "id": "rental_cashflow",
            "title": "Kira Getirisi ve Nakit Akışı",
            "commercial": False,
            "items": [
                "Kira çarpanı",
                "Gerçek kira değeri",
                "Daire karşılaştırması",
                "Kira tahsilat riski",
                "Kredi durumu",
                "Kısa dönem kiralama potansiyeli",
                "Beklenen bakım bütçesi",
                "Büyük bakım döngüleri",
                "Kiralanabilirlik puanı",
                "Daire kullanım verimliliği",
                "Bölge kira artış geçmişi",
                "Alternatif yatırım getirisi",
                "Satın alma maliyeti",
                "Toplam mülkiyet değeri",
                "Aylık ödeme gücüne göre kira oranı",
                "Net kira verimi",
                "Kaldıraç oranı",
                "Peşinat durumu",
                "Krediye uygunluk",
                "Kredi sigortası etkisi",
                "İlan süresi",
                "Benzer ilan karşılaştırması",
            ],
        },
        {
            "id": "commercial_location",
            "title": "İş Yeri — Lokasyon ve Görünürlük",
            "commercial": True,
            "items": [
                "Ana cadde cephe uzunluğu",
                "Yaya trafik yoğunluğu",
                "Araç trafik yoğunluğu",
                "Tabela görünürlük açısı",
                "Köşebaşı / şerefiye avantajı",
                "Hedef kitle demografisi",
                "Rakip işletmelere mesafe",
                "Tamamlayıcı işletme sinerjisi",
                "Toplu taşımaya uzaklık",
                "Büyük çekim merkezlerine yakınlık",
                "Bölgesel güvenlik algısı",
                "Mahalle / semt marka değeri",
            ],
        },
        {
            "id": "commercial_space",
            "title": "İş Yeri — Lojistik ve Fiziksel Alan",
            "commercial": True,
            "items": [
                "Net kullanılabilir zemin alanı",
                "Brüt / net metrekare oranı",
                "Tavan yüksekliği",
                "Depo hacmi",
                "Mal indirme / bindirme alanı",
                "Otopark kapasitesi",
                "Yangın çıkışları ve tahliye",
            ],
        },
        {
            "id": "commercial_finance_legal",
            "title": "İş Yeri — Finansal Uygunluk ve Yasal Durum",
            "commercial": True,
            "items": [
                "Aylık net kira",
                "Bölgesel emsal kira karşılaştırması",
                "Amortisman süresi",
                "Sözleşme süresi ve güvence",
                "Tapu niteliği",
                "İskan / ruhsat ve imar uygunluğu",
                "Yangın ve deprem yönetmeliği uygunluğu",
            ],
        },
    ],
}


def build() -> dict:
    categories = []
    for cat in INVENTORY["categories"]:
        items = []
        seen: set[str] = set()
        for label in cat["items"]:
            item_id = f"{cat['id']}__{slug(label)}"
            if item_id in seen:
                continue
            seen.add(item_id)
            items.append({"id": item_id, "label": label})
        categories.append(
            {
                "id": cat["id"],
                "title": cat["title"],
                "commercial": bool(cat["commercial"]),
                "items": items,
            }
        )
    return {
        "version": INVENTORY["version"],
        "source": INVENTORY["source"],
        "categories": categories,
    }


def main() -> None:
    payload = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    n_items = sum(len(c["items"]) for c in payload["categories"])
    print(f"Wrote {OUT} ({len(payload['categories'])} categories, {n_items} items)")


if __name__ == "__main__":
    main()
