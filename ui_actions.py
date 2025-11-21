#!/usr/bin/env python3
"""
UI otomasyon aksiyonları modülü
"""

import time
import uiautomator2 as u2


def init_ui_automator(device_id):
    """UIAutomator2 bağlantısını başlatır"""
    try:
        print("\n--- UI Otomasyon Hazırlanıyor ---")
        d = u2.connect(device_id)
        print(f"✓ UI otomasyon bağlantısı kuruldu")
        return d
    except Exception as e:
        print(f"✗ UI otomasyon bağlantısı kurulamadı: {e}")
        return None


def close_cookie_dialog(d):
    """Çerez tercih dialogunu kapatır"""
    print("\n--- Çerez Dialogunu Kapatıyor ---")
    try:
        # Çeşitli olası buton metinlerini dene
        possible_buttons = [
            "Tüm Çerezleri Reddet",
            "TÜM ÇEREZLERİ REDDET",
            "Reddet",
            "REDDET",
            "Kabul Et",
            "KABUL ET",
            "Tamam",
            "TAMAM",
            "Anladım",
            "ANLADIM",
            "Devam Et",
            "DEVAM ET",
            "Kapat",
            "KAPAT",
            "Accept",
            "OK"
        ]
        
        # 3 saniye bekle - dialog'un açılması için
        time.sleep(3)
        
        # Her bir buton metnini dene
        for button_text in possible_buttons:
            if d(text=button_text).exists(timeout=2):
                print(f"✓ '{button_text}' butonu bulundu, tıklanıyor...")
                d(text=button_text).click()
                time.sleep(1)
                print(f"✓ Çerez dialogu kapatıldı")
                return True
        
        # textContains ile dene (kısmi eşleşme)
        if d(textContains="Reddet").exists(timeout=2):
            print(f"✓ 'Reddet' içeren buton bulundu, tıklanıyor...")
            d(textContains="Reddet").click()
            time.sleep(1)
            print(f"✓ Çerez dialogu kapatıldı")
            return True
        
        # Resource ID ile de dene
        if d(resourceId="com.sahibinden:id/rejectButton").exists(timeout=2):
            print(f"✓ Reddet butonu (ID ile) bulundu, tıklanıyor...")
            d(resourceId="com.sahibinden:id/rejectButton").click()
            time.sleep(1)
            print(f"✓ Çerez dialogu kapatıldı")
            return True
        
        if d(resourceId="com.sahibinden:id/acceptButton").exists(timeout=2):
            print(f"✓ Kabul butonu (ID ile) bulundu, tıklanıyor...")
            d(resourceId="com.sahibinden:id/acceptButton").click()
            time.sleep(1)
            print(f"✓ Çerez dialogu kapatıldı")
            return True
        
        print("⚠️  Çerez dialogu bulunamadı (zaten kapalı olabilir)")
        return True
        
    except Exception as e:
        print(f"⚠️  Çerez dialogu kapatılırken hata: {e}")
        # Hata olsa bile devam et
        return True


def scroll_to_top(d):
    """Sayfayı en üste kaydırır"""
    print("  → Sayfa en üste kaydırılıyor...")
    try:
        # Ekran boyutlarını al
        width, height = d.window_size()
        center_x = width // 2
        
        # Birkaç kez yukarı doğru swipe yap (en üste ulaşmak için)
        for i in range(5):
            # Ekranın üst kısmından başlayıp daha da yukarı swipe yap
            start_y = int(height * 0.2)  # Ekranın %20'sinden başla
            end_y = int(height * 0.8)    # Ekranın %80'ine kadar swipe yap (yukarı kaydırma)
            
            d.swipe(center_x, start_y, center_x, end_y, duration=0.3)
            time.sleep(0.5)
        
        time.sleep(1)
        print("  ✓ Sayfa en üste kaydırıldı")
        return True
    except Exception as e:
        print(f"  ⚠️  Sayfa üste kaydırılırken hata: {e}")
        return True  # Hata olsa bile devam et


def click_category(d, name):
    """{name} kategorisine tıklar - önce en üste scroll yapar, sonra aşağı kaydırarak arar"""
    print(f"\n--- {name} Kategorisine Tıklanıyor ---")
    time.sleep(4)
    
    # Önce sayfayı en üste kaydır
    scroll_to_top(d)
    time.sleep(1)
    
    try:
        # Scroll edilebilir container bul
        scrollable = d(scrollable=True)
        max_scrolls = 50  # Maksimum scroll sayısı
        scroll_attempts = 0
        
        print(f"  → '{name}' kategorisi aranıyor (aşağı doğru scroll ile)...")
        
        while scroll_attempts < max_scrolls:
            # Önce mevcut ekranda kategoriyi ara
            # 1. Text ile arama
            if d(text=name).exists(timeout=1):
                print(f"✓ '{name}' kategorisi bulundu (text ile)")
                d(text=name).click()
                time.sleep(2)
                print(f"✓ '{name}' kategorisine tıklandı")
                return True
            
            # 2. Büyük harf ile
            if d(text=name.upper()).exists(timeout=1):
                print(f"✓ '{name.upper()}' kategorisi bulundu")
                d(text=name.upper()).click()
                time.sleep(2)
                print(f"✓ '{name.upper()}' kategorisine tıklandı")
                return True
            
            # 3. textContains ile
            if d(textContains=name).exists(timeout=1):
                print(f"✓ '{name}' içeren kategori bulundu")
                d(textContains=name).click()
                time.sleep(2)
                print(f"✓ '{name}' kategorisine tıklandı")
                return True
            
            # 4. description ile
            if d(description=name).exists(timeout=1):
                print(f"✓ '{name}' kategorisi bulundu (description ile)")
                d(description=name).click()
                time.sleep(2)
                print(f"✓ '{name}' kategorisine tıklandı")
                return True
            
            # Kategori bulunamadı, aşağı doğru scroll yap
            try:
                # Ekran boyutlarını al
                width, height = d.window_size()
                center_x = width // 2
                start_y = int(height * 0.6)  # Ekranın %60'ından başla
                end_y = int(height * 0.3)    # Ekranın %30'una kadar swipe yap (aşağı kaydırma)
                
                # Smooth swipe (aşağı doğru)
                d.swipe(center_x, start_y, center_x, end_y, duration=0.5)
            except Exception as e:
                # Swipe başarısız olursa fallback olarak scroll kullan
                try:
                    if scrollable.exists(timeout=1):
                        scrollable.scroll.vert.forward(steps=1)
                except:
                    pass
            
            time.sleep(1.5)  # Scroll sonrası bekleme süresi
            scroll_attempts += 1
            
            # Her 10 scroll'da bir ilerleme göster
            if scroll_attempts % 10 == 0:
                print(f"  → İlerleme: {scroll_attempts} scroll yapıldı, '{name}' aranıyor...")
        
        if scroll_attempts >= max_scrolls:
            print(f"  ⚠️  Maksimum scroll sayısına ulaşıldı ({max_scrolls})")
        
        print(f"✗ '{name}' kategorisi bulunamadı ({scroll_attempts} scroll yapıldı)")
        print("💡 Ekran XML'ini kontrol edebilirsiniz: adb shell uiautomator dump")
        return False
        
    except Exception as e:
        print(f"✗ '{name}' kategorisine tıklanırken hata: {e}")
        return False

def click_vasita_category(d):
    """Vasıta kategorisine tıklar"""
    print("\n--- Vasıta Kategorisine Tıklanıyor ---")
    return click_category(d, "Vasıta")

def click_otomobil_category(d):
    """Otomobil kategorisine tıklar"""
    print("\n--- Otomobil Kategorisine Tıklanıyor ---")
    return click_category(d, "Otomobil")


def click_tum_button(d, category_name):
    """'Tüm {category_name} İlanları' yazan butona tıklar"""
    print(f"\n--- 'Tüm {category_name} İlanları' Butonuna Tıklanıyor ---")
    time.sleep(4)
    try:
        # Önce sayfayı en üste kaydır
        scroll_to_top(d)
        time.sleep(1)
        
        # Olası "Tüm {category_name} İlanları" buton metinleri
        possible_texts = [
            f"Tüm {category_name} İlanları",
            f"TÜM {category_name.upper()} İLANLARI",
            f"Tüm {category_name} İlanları",
            f"Tüm '{category_name}' İlanları",
            f"TÜM '{category_name.upper()}' İLANLARI",
            f"Tüm \"{category_name}\" İlanları",
            f"TÜM \"{category_name.upper()}\" İLANLARI"
        ]
        
        # Scroll edilebilir container bul
        scrollable = d(scrollable=True)
        max_scrolls = 20  # Maksimum scroll sayısı
        scroll_attempts = 0
        
        print(f"  → 'Tüm {category_name} İlanları' butonu aranıyor (aşağı doğru scroll ile)...")
        
        while scroll_attempts < max_scrolls:
            # Önce mevcut ekranda butonu ara
            for text in possible_texts:
                if d(text=text).exists(timeout=1):
                    print(f"✓ '{text}' butonu bulundu (text ile)")
                    d(text=text).click()
                    time.sleep(2)
                    print(f"✓ '{text}' butonuna tıklandı")
                    return True
            
            # textContains ile kategori ismini içeren "Tüm" butonunu ara
            if d(textContains="Tüm").exists(timeout=1) and d(textContains=category_name).exists(timeout=1):
                # XML dump alarak tam eşleşmeyi bul
                try:
                    xml_content = d.dump_hierarchy()
                    from lxml import etree
                    
                    try:
                        root = etree.fromstring(xml_content.encode('utf-8'))
                    except:
                        root = etree.fromstring(xml_content)
                    
                    # Tüm elementleri gez ve "Tüm" ve kategori ismini içeren ilk clickable elementi bul
                    for elem in root.iter():
                        attrib = elem.attrib
                        text = attrib.get('text', '').strip()
                        clickable = attrib.get('clickable', 'false').lower() == 'true'
                        
                        if text and clickable:
                            text_lower = text.lower()
                            category_lower = category_name.lower()
                            if 'tüm' in text_lower and category_lower in text_lower and 'ilan' in text_lower:
                                print(f"✓ 'Tüm {category_name} İlanları' butonu bulundu: '{text}'")
                                d(text=text).click()
                                time.sleep(2)
                                print(f"✓ '{text}' butonuna tıklandı")
                                return True
                except Exception as e:
                    print(f"  ⚠️  XML parse sırasında hata: {e}")
            
            # Buton bulunamadı, aşağı doğru scroll yap
            try:
                # Ekran boyutlarını al
                width, height = d.window_size()
                center_x = width // 2
                start_y = int(height * 0.6)  # Ekranın %60'ından başla
                end_y = int(height * 0.3)    # Ekranın %30'una kadar swipe yap (aşağı kaydırma)
                
                # Smooth swipe (aşağı doğru)
                d.swipe(center_x, start_y, center_x, end_y, duration=0.5)
            except Exception as e:
                # Swipe başarısız olursa fallback olarak scroll kullan
                try:
                    if scrollable.exists(timeout=1):
                        scrollable.scroll.vert.forward(steps=1)
                except:
                    pass
            
            time.sleep(1.5)  # Scroll sonrası bekleme süresi
            scroll_attempts += 1
            
            # Her 5 scroll'da bir ilerleme göster
            if scroll_attempts % 5 == 0:
                print(f"  → İlerleme: {scroll_attempts} scroll yapıldı, 'Tüm {category_name} İlanları' aranıyor...")
        
        if scroll_attempts >= max_scrolls:
            print(f"  ⚠️  Maksimum scroll sayısına ulaşıldı ({max_scrolls})")
        
        print(f"✗ 'Tüm {category_name} İlanları' butonu bulunamadı ({scroll_attempts} scroll yapıldı)")
        print("💡 Ekran XML'ini kontrol edebilirsiniz: adb shell uiautomator dump")
        return False
        
    except Exception as e:
        print(f"✗ 'Tüm {category_name} İlanları' butonuna tıklanırken hata: {e}")
        return False