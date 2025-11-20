#!/usr/bin/env python3
"""
Kategori okuma modülü - Vasıta sayfasındaki kategorileri okur
"""

import time

# Öncelikli kategoriler (markalar) - case-insensitive
PRIORITY_CATEGORIES = [
    'honda', 'hyundai', 'renault', 'opel', 'audi', 'mercedes', 
    'bmw', 'citroen', 'chery', 'fiat', 'dacia', 'ford', 'kia', 
    'peugeut', 'skoda', 'seat', 'toyota', 'volkswagen', 'volvo'
]


def read_categories_from_page(d):
    """Vasıta sayfasındaki tüm kategorileri okur"""
    print("\n--- Kategoriler Okunuyor ---")
    try:
        # Sayfanın yüklenmesi için bekle
        time.sleep(3)
        
        categories = []
        
        # Çeşitli yöntemlerle kategorileri bulmaya çalış
        
        # 1. Resource ID ile kategori listesi bulmaya çalış
        # Sahibinden uygulamasında kategoriler genellikle RecyclerView veya ListView içinde olur
        try:
            # XML dump alarak kategorileri bulabiliriz
            xml = d.dump_hierarchy()
            
            # Text içeren tüm elementleri al
            all_elements = d.dump_hierarchy()
            
            # Kategoriler genellikle TextView veya clickable elementler olur
            # Farklı selector'ları dene
            
            # Text ile kategori isimlerini bul
            # Kategori isimleri genellikle belirli bir pattern'e sahiptir
            # Örnek: "Otomobil", "Motosiklet", "Minivan", vb.
            
            # Scroll edilebilir bir liste varsa, scroll yaparak tüm kategorileri oku
            # Önce scroll edilebilir container'ı bul
            
            # UIAutomator2 ile tüm text elementlerini al
            # Ancak bu çok fazla element döndürebilir, filtreleme gerekir
            
            # Daha spesifik bir yaklaşım: Kategori listesi genellikle belirli bir resource ID'ye sahiptir
            # veya belirli bir class'a sahiptir
            
            # Basit yaklaşım: Ekrandaki tüm text'leri al ve filtrele
            # Ancak bu çok fazla noise içerebilir
            
            # Daha iyi yaklaşım: Scroll yaparak tüm kategorileri topla
            print("  Kategoriler scroll edilerek okunuyor...")
            
            # Scroll edilebilir container bul
            scrollable = d(scrollable=True)
            if scrollable.exists(timeout=2):
                print("  ✓ Scroll edilebilir container bulundu")
                
                # Scroll başlangıcı
                previous_categories = set()
                scroll_attempts = 0
                max_scrolls = 10
                
                while scroll_attempts < max_scrolls:
                    # Mevcut ekrandaki kategorileri oku
                    current_categories = extract_categories_from_screen(d)
                    
                    # Yeni kategori var mı kontrol et
                    if current_categories.issubset(previous_categories):
                        # Yeni kategori yok, scroll bitmiş olabilir
                        break
                    
                    # Yeni kategorileri ekle
                    for cat in current_categories:
                        if cat not in previous_categories:
                            categories.append(cat)
                            print(f"  ✓ Kategori bulundu: {cat}")
                    
                    previous_categories.update(current_categories)
                    
                    # Aşağı scroll yap
                    scrollable.scroll.vert.backward(steps=10)
                    time.sleep(1)
                    scroll_attempts += 1
                
                print(f"  ✓ Toplam {len(categories)} kategori bulundu")
            else:
                # Scroll edilebilir container yoksa, direkt ekrandaki kategorileri oku
                print("  ⊙ Scroll edilebilir container bulunamadı, ekrandaki kategoriler okunuyor...")
                categories = list(extract_categories_from_screen(d))
                print(f"  ✓ {len(categories)} kategori bulundu")
            
        except Exception as e:
            print(f"  ⚠️  Kategori okuma sırasında hata: {e}")
            # Fallback: Basit text extraction
            categories = list(extract_categories_from_screen(d))
        
        # Kategorileri temizle ve filtrele
        # Boş string'leri, sayıları ve gereksiz text'leri filtrele
        filtered_categories = []
        exclude_keywords = ['Vasıta', 'Kategori', 'Ara', 'Filtre', 'Sırala', 'Menü', 'Geri', 'İleri']
        
        for cat in categories:
            cat = cat.strip()
            if cat and len(cat) > 2:  # En az 3 karakter
                # Exclude keywords içermiyorsa ekle
                if not any(keyword.lower() in cat.lower() for keyword in exclude_keywords):
                    # Sayı değilse ekle
                    if not cat.isdigit():
                        filtered_categories.append(cat)
        
        # Duplicate'leri kaldır ama sırayı koru
        seen = set()
        unique_categories = []
        for cat in filtered_categories:
            if cat not in seen:
                seen.add(cat)
                unique_categories.append(cat)
        
        # Kategorileri öncelik sırasına göre sırala
        sorted_categories = sort_categories_by_priority(unique_categories)
        
        print(f"\n✓ Toplam {len(sorted_categories)} benzersiz kategori bulundu")
        print(f"  - Öncelikli: {len([c for c in sorted_categories if is_priority_category(c)])}")
        print(f"  - Diğerleri: {len([c for c in sorted_categories if not is_priority_category(c)])}")
        return sorted_categories
        
    except Exception as e:
        print(f"✗ Kategori okuma sırasında hata: {e}")
        return []


def extract_categories_from_screen(d):
    """Ekrandaki kategorileri çıkarır"""
    categories = set()
    
    try:
        # XML hierarchy'yi al ve parse et
        xml_content = d.dump_hierarchy()
        
        # XML'i parse etmek için lxml kullanabiliriz
        from lxml import etree
        
        # XML string'i parse et
        # UIAutomator2'nin dump_hierarchy() metodu XML string döndürür
        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
        except:
            # Eğer encoding sorunu varsa, direkt string olarak dene
            root = etree.fromstring(xml_content)
        
        # Tüm node'ları bul ve text içerenleri topla
        # Kategori item'ları genellikle clickable ve text içerir
        # Resource ID'de "category", "item", "list", "row" gibi kelimeler olabilir
        
        # Tüm elementleri gez
        for elem in root.iter():
            # Attribute'ları al
            attrib = elem.attrib
            
            # Text içeren elementleri bul
            text = attrib.get('text', '').strip()
            content_desc = attrib.get('content-desc', '').strip()
            resource_id = attrib.get('resource-id', '').lower()
            clickable = attrib.get('clickable', 'false').lower() == 'true'
            
            # Kategori olabilecek text'leri topla
            # Kategori genellikle clickable ve text içerir
            # Resource ID'de kategori ile ilgili kelimeler olabilir
            if text:
                # Basit filtreleme: çok kısa veya sayı olan text'leri atla
                if len(text) > 2 and not text.isdigit():
                    # Bazı UI elementlerini filtrele
                    if not any(exclude in text.lower() for exclude in 
                              ['vasıta', 'kategori', 'ara', 'filtre', 'sırala', 
                               'menü', 'geri', 'ileri', 'aç', 'kapat', 'tamam', 'iptal',
                               'giriş', 'kayıt', 'profil', 'ayarlar', 'yardım']):
                        categories.add(text)
            
            # Content description'dan da kategori bulabiliriz
            if content_desc and len(content_desc) > 2:
                if not content_desc.isdigit():
                    if not any(exclude in content_desc.lower() for exclude in 
                              ['vasıta', 'kategori', 'ara', 'filtre', 'sırala',
                               'menü', 'geri', 'ileri', 'aç', 'kapat']):
                        categories.add(content_desc)
        
    except Exception as e:
        print(f"  ⚠️  XML parse sırasında hata: {e}")
        # Fallback: Basit text extraction - UIAutomator2 selector kullan
        try:
            # Tüm görünür text elementlerini al (yavaş ama çalışır)
            # Bu çok fazla element döndürebilir, bu yüzden dikkatli kullan
            print("  ⊙ XML parse başarısız, alternatif yöntem deneniyor...")
        except:
            pass
    
    return categories


def is_priority_category(category):
    """Kategorinin öncelikli olup olmadığını kontrol eder (case-insensitive)"""
    category_lower = category.lower().strip()
    return category_lower in PRIORITY_CATEGORIES


def get_category_priority(category):
    """Kategorinin öncelik sırasını döndürür (düşük sayı = yüksek öncelik)"""
    category_lower = category.lower().strip()
    try:
        return PRIORITY_CATEGORIES.index(category_lower)
    except ValueError:
        # Öncelikli değilse, en sona koy (yüksek sayı)
        return len(PRIORITY_CATEGORIES) + 1000


def sort_categories_by_priority(categories):
    """Kategorileri öncelik sırasına göre sıralar"""
    # Önce öncelik sırasına göre, sonra alfabetik olarak sırala
    sorted_list = sorted(categories, key=lambda cat: (get_category_priority(cat), cat.lower()))
    return sorted_list


def read_vasita_categories(d):
    """Vasıta sayfasındaki kategorileri okur ve döndürür"""
    return read_categories_from_page(d)

