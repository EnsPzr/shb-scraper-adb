#!/usr/bin/env python3
"""
Kategori okuma modülü - Vasıta sayfasındaki kategorileri okur
"""

import time

# Öncelikli kategoriler (markalar) - case-insensitive
PRIORITY_CATEGORIES = [
    'honda', 'hyundai', 'renault', 'opel', 'audi', 'mercedes-benz', 
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
                
                # İlk okuma - başlangıç kategorileri
                print("  → İlk okuma yapılıyor...")
                
                # İlk okumada "Navigasyon Cihazı" kontrolü
                if check_navigation_device_header(d):
                    print("  → 'Navigasyon Cihazı' zaten görünüyor, kategori okunmayacak")
                    return []
                
                current_categories = extract_categories_from_screen(d)
                # "Navigasyon Cihazı" başlığını filtrele
                current_categories = {cat for cat in current_categories 
                                   if not is_navigation_device_header(cat)}
                
                for cat in current_categories:
                    categories.append(cat)
                    print(f"  ✓ Kategori bulundu: {cat}")
                
                previous_categories = set(current_categories)
                scroll_attempts = 0
                no_new_categories_count = 0
                max_no_new_categories = 3  # 3 kez üst üste yeni kategori yoksa dur
                max_scrolls = 100  # Maksimum scroll sayısı (güvenlik için)
                
                print(f"  → Scroll başlatılıyor (maksimum {max_scrolls} scroll)...")
                
                while scroll_attempts < max_scrolls:
                    # "Navigasyon Cihazı" başlığına gelip gelmediğini kontrol et
                    if check_navigation_device_header(d):
                        print("  → 'Navigasyon Cihazı' görüldü, okuma durduruluyor")
                        break
                    
                    # Smooth scroll için swipe kullan (ekranın ortasından aşağı doğru)
                    # Bu şekilde elementlere tıklamadan sadece scroll yapar
                    try:
                        # Ekran boyutlarını al
                        width, height = d.window_size()
                        center_x = width // 2
                        start_y = int(height * 0.6)  # Ekranın %60'ından başla
                        end_y = int(height * 0.3)    # Ekranın %30'una kadar swipe yap
                        
                        # Smooth swipe (duration uzun olursa daha smooth)
                        d.swipe(center_x, start_y, center_x, end_y, duration=0.5)
                    except Exception as e:
                        # Swipe başarısız olursa fallback olarak scroll kullan
                        try:
                            scrollable.scroll.vert.forward(steps=1)
                        except:
                            pass
                    
                    time.sleep(1.5)  # Scroll sonrası bekleme süresi
                    
                    # Scroll sonrası tekrar kontrol et
                    if check_navigation_device_header(d):
                        print("  → 'Navigasyon Cihazı' görüldü, okuma durduruluyor")
                        break
                    
                    # Mevcut ekrandaki kategorileri oku
                    current_categories = extract_categories_from_screen(d)
                    
                    # "Navigasyon Cihazı" başlığını kategorilerden çıkar
                    current_categories = {cat for cat in current_categories 
                                        if not is_navigation_device_header(cat)}
                    
                    # Yeni kategorileri bul
                    new_categories = current_categories - previous_categories
                    
                    if new_categories:
                        # Yeni kategori var
                        no_new_categories_count = 0
                        for cat in new_categories:
                            # "Navigasyon Cihazı" başlığını ekleme
                            if not is_navigation_device_header(cat):
                                categories.append(cat)
                                print(f"  ✓ Kategori bulundu: {cat}")
                        previous_categories.update(current_categories)
                    else:
                        # Yeni kategori yok
                        no_new_categories_count += 1
                        print(f"  ⊙ Yeni kategori bulunamadı ({no_new_categories_count}/{max_no_new_categories})")
                        
                        # Eğer birkaç kez üst üste yeni kategori yoksa, sayfa sonuna gelmiş olabiliriz
                        if no_new_categories_count >= max_no_new_categories:
                            print("  → Sayfa sonuna gelindi (yeni kategori yok)")
                            break
                    
                    scroll_attempts += 1
                    
                    # Her 10 scroll'da bir ilerleme göster
                    if scroll_attempts % 10 == 0:
                        print(f"  → İlerleme: {scroll_attempts} scroll, {len(categories)} kategori bulundu")
                
                if scroll_attempts >= max_scrolls:
                    print(f"  ⚠️  Maksimum scroll sayısına ulaşıldı ({max_scrolls})")
                
                print(f"  ✓ Toplam {len(categories)} kategori bulundu ({scroll_attempts} scroll yapıldı)")
            else:
                # Scroll edilebilir container yoksa, direkt ekrandaki kategorileri oku
                print("  ⊙ Scroll edilebilir container bulunamadı, ekrandaki kategoriler okunuyor...")
                categories = list(extract_categories_from_screen(d))
                print(f"  ✓ {len(categories)} kategori bulundu")
            
        except Exception as e:
            print(f"  ⚠️  Kategori okuma sırasında hata: {e}")
            # Fallback: Basit text extraction
            categories = list(extract_categories_from_screen(d))
        
        # Kategorileri temizle ve filtrele (extract_categories_from_screen zaten filtreleme yapıyor)
        # Ekstra temizlik için
        filtered_categories = []
        exclude_keywords = ['Vasıta', 'Kategori seçimi', 'Tüm', 'İlanları']
        
        for cat in categories:
            cat = cat.strip()
            if cat and len(cat) > 2:  # En az 3 karakter
                cat_lower = cat.lower()
                
                # Ekstra filtreleme
                # "Tüm 'Otomobil' İlanları" gibi text'leri atla
                if 'tüm' in cat_lower and 'ilan' in cat_lower:
                    continue
                
                # "Navigasyon Cihazı" başlığını atla
                if is_navigation_device_header(cat):
                    continue
                
                # Exclude keywords içermiyorsa ekle
                if not any(keyword.lower() in cat_lower for keyword in exclude_keywords):
                    # Sadece sayı değilse ekle
                    if not cat.replace(' ', '').isdigit():
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
    """Ekrandaki kategorileri çıkarır - sadece marka/kategori isimlerini"""
    categories = set()
    
    try:
        # XML hierarchy'yi al ve parse et
        xml_content = d.dump_hierarchy()
        
        # XML'i parse etmek için lxml kullanabiliriz
        from lxml import etree
        
        # XML string'i parse et
        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
        except:
            # Eğer encoding sorunu varsa, direkt string olarak dene
            root = etree.fromstring(xml_content)
        
        # Filtreleme için exclude listeleri
        exclude_keywords = [
            'vasıta', 'kategori', 'ara', 'filtre', 'sırala', 'menü', 'geri', 'ileri',
            'aç', 'kapat', 'tamam', 'iptal', 'giriş', 'kayıt', 'profil', 'ayarlar',
            'yardım', 'back', 'home', 'overview', 'seçimi', 'tüm'
        ]
        
        # Sistem mesajları
        system_messages = [
            'wifi', 'signal', 'battery', 'charging', 'percent', 'phone', 'full',
            'pm', 'am', ':', 'overview'
        ]
        
        # Tüm elementleri gez
        for elem in root.iter():
            attrib = elem.attrib
            text = attrib.get('text', '').strip()
            content_desc = attrib.get('content-desc', '').strip()
            resource_id = attrib.get('resource-id', '').lower()
            clickable = attrib.get('clickable', 'false').lower() == 'true'
            class_name = attrib.get('class', '').lower()
            
            # Text'i kontrol et
            if text:
                text_lower = text.lower()
                
                # 1. Çok kısa text'leri atla (2 karakter veya daha az)
                if len(text) <= 2:
                    continue
                
                # 2. Sadece sayı içeren text'leri atla (parantez içindeki sayılar)
                if text.startswith('(') and text.endswith(')'):
                    continue
                
                # 3. Sadece rakam ve nokta içeren text'leri atla (396.611 gibi)
                if all(c.isdigit() or c in '.,()' for c in text):
                    continue
                
                # 4. Zaman formatlarını atla (7:20, 7:20 PM gibi)
                if ':' in text and any(c.isdigit() for c in text):
                    if 'pm' in text_lower or 'am' in text_lower or len(text) <= 6:
                        continue
                
                # 5. Sistem mesajlarını atla
                if any(msg in text_lower for msg in system_messages):
                    continue
                
                # 6. UI elementlerini atla
                if any(exclude in text_lower for exclude in exclude_keywords):
                    continue
                
                # 7. "Navigasyon Cihazı" başlığını atla
                if is_navigation_device_header(text):
                    continue
                
                # 7. Sadece harf, boşluk ve bazı özel karakterler içermeli (marka isimleri için)
                # Sayı içermemeli (marka isimleri genellikle sadece harf içerir)
                if text.replace(' ', '').replace('&', '').replace('-', '').replace("'", '').isdigit():
                    continue
                
                # 8. En az bir harf içermeli
                if not any(c.isalpha() for c in text):
                    continue
                
                # 9. Resource ID'de "item", "row", "category" gibi kelimeler varsa daha güvenilir
                # Ama zorunlu değil, çünkü bazı uygulamalarda farklı olabilir
                
                # Kategori olarak ekle
                categories.add(text)
            
            # Content description'dan da kategori bulabiliriz (daha az güvenilir)
            if content_desc and len(content_desc) > 2:
                content_desc_lower = content_desc.lower()
                
                # Aynı filtrelemeleri uygula
                if (not content_desc.startswith('(') and 
                    not all(c.isdigit() or c in '.,()' for c in content_desc) and
                    ':' not in content_desc and
                    not any(msg in content_desc_lower for msg in system_messages) and
                    not any(exclude in content_desc_lower for exclude in exclude_keywords) and
                    any(c.isalpha() for c in content_desc)):
                    categories.add(content_desc)
        
    except Exception as e:
        print(f"  ⚠️  XML parse sırasında hata: {e}")
        # Fallback: Basit text extraction
        try:
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


def is_navigation_device_header(text):
    """Text'in 'Navigasyon Cihazı' veya 'Navigasyon Cihazları' olup olmadığını kontrol eder"""
    text_lower = text.lower().strip()
    navigation_keywords = [
        'navigasyon cihazı', 
        'navigasyon cihazları', 
        'navigasyon cihazi',
        'navigasyon cihazlari',
        'navigation device',
        'navigation devices'
    ]
    return any(keyword in text_lower for keyword in navigation_keywords)


def check_navigation_device_header(d):
    """Ekranda 'Navigasyon Cihazı' veya 'Navigasyon Cihazları' olup olmadığını kontrol eder"""
    try:
        # XML dump al ve kontrol et
        xml_content = d.dump_hierarchy()
        from lxml import etree
        
        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
        except:
            root = etree.fromstring(xml_content)
        
        # Tüm text'leri kontrol et
        for elem in root.iter():
            attrib = elem.attrib
            text = attrib.get('text', '').strip()
            content_desc = attrib.get('content-desc', '').strip()
            
            if text and is_navigation_device_header(text):
                return True
            if content_desc and is_navigation_device_header(content_desc):
                return True
        
        return False
    except Exception as e:
        # Hata durumunda False döndür (güvenli taraf)
        return False


def read_vasita_categories(d):
    """Vasıta sayfasındaki kategorileri okur ve döndürür"""
    return read_categories_from_page(d)

