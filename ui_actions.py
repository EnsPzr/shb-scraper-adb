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


def click_category(d, name):
    """Vasıta kategorisine tıklar"""
    print("\n--- Vasıta Kategorisine Tıklanıyor ---")
    try:
        # Çeşitli olası yolları dene
        
        # 1. Text ile arama
        if d(text=name).exists(timeout=3):
            print(f"✓ '{name}' kategorisi bulundu (text ile)")
            d(text=name).click()
            time.sleep(2)
            print(f"✓ '{name}' kategorisine tıklandı")
            return True
        
        # 2. VASITA (büyük harf)
        if d(text=name.upper()).exists(timeout=3):
            print(f"✓ '{name.upper()}' kategorisi bulundu")
            d(text=name.upper()).click()
            time.sleep(2)
            print(f"✓ '{name.upper()}' kategorisine tıklandı")
            return True
        
        # 3. textContains ile
        if d(textContains=name).exists(timeout=3):
            print(f"✓ '{name}' içeren kategori bulundu")
            d(textContains=name).click()
            time.sleep(2)
            print(f"✓ '{name}' kategorisine tıklandı")
            return True
        
        # 4. description ile
        if d(description=name).exists(timeout=3):
            print(f"✓ '{name}' kategorisi bulundu (description ile)")
            d(description=name).click()
            time.sleep(2)
            print(f"✓ '{name}' kategorisine tıklandı")
            return True
        
        print(f"✗ '{name}' kategorisi bulunamadı")
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