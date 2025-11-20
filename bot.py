#!/usr/bin/env python3
"""
Sahibinden Bot sınıfı
"""

from device import check_adb, connect_device
from app import launch_app
from ui_actions import init_ui_automator, close_cookie_dialog, click_vasita_category
from category_reader import read_vasita_categories
from database import run_migration, save_categories


class SahibindenBot:
    """Sahibinden uygulaması için otomasyon sınıfı"""
    
    def __init__(self):
        """Bot'u başlatır ve ADB bağlantısını kontrol eder"""
        self.device_id = None
        self.d = None  # uiautomator2 device instance
        
    def check_adb(self):
        """ADB'nin kurulu olup olmadığını kontrol eder"""
        return check_adb()
    
    def get_connected_devices(self):
        """Bağlı cihazları listeler"""
        from device import get_connected_devices
        return get_connected_devices()
    
    def connect_device(self):
        """Cihaza bağlanır"""
        self.device_id = connect_device()
        return self.device_id is not None
    
    def is_app_installed(self):
        """Sahibinden uygulamasının kurulu olup olmadığını kontrol eder"""
        from app import is_app_installed
        return is_app_installed(self.device_id)
    
    def launch_app(self):
        """Sahibinden uygulamasını açar"""
        return launch_app(self.device_id)
    
    def init_ui_automator(self):
        """UIAutomator2 bağlantısını başlatır"""
        self.d = init_ui_automator(self.device_id)
        return self.d is not None
    
    def close_cookie_dialog(self):
        """Çerez tercih dialogunu kapatır"""
        return close_cookie_dialog(self.d)
    
    def click_vasita_category(self):
        """Vasıta kategorisine tıklar"""
        return click_vasita_category(self.d)
    
    def run(self):
        """Ana çalıştırma fonksiyonu"""
        print("=" * 50)
        print("Sahibinden Mobilden Otomasyonu")
        print("=" * 50)
        
        # Veritabanı migration
        print("\n--- Veritabanı Hazırlanıyor ---")
        if not run_migration():
            print("⚠️  Veritabanı migration başarısız, devam ediliyor...")
        
        # ADB kontrolü
        if not self.check_adb():
            return False
        
        # Cihaz bağlantısı
        if not self.connect_device():
            return False
        
        # Uygulamayı başlat
        if not self.launch_app():
            return False
        
        # UI otomasyon hazırla
        if not self.init_ui_automator():
            return False
        
        # Çerez dialogunu kapat
        #if not self.close_cookie_dialog():
        #    print("⚠️  Çerez dialogu kapatılamadı ama devam ediliyor...")
        
        # Vasıta kategorisine tıkla
        if not self.click_vasita_category():
            return False

        if not self.click_otomobil_category():
            return False
        
        # Kategorileri oku
        categories = read_vasita_categories(self.d)
        
        if not categories:
            print("⚠️  Hiç kategori bulunamadı")
            return False
        
        # Kategorileri veritabanına kaydet
        print("\n--- Kategoriler Veritabanına Kaydediliyor ---")
        if not save_categories(categories, self.device_id, page=1):
            print("⚠️  Kategoriler kaydedilemedi")
            return False
        
        print("\n" + "=" * 50)
        print("✓ İşlem tamamlandı!")
        print("=" * 50)
        return True

