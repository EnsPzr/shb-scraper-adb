#!/usr/bin/env python3
"""
Sahibinden Bot sınıfı
"""

import os
import time

from device import check_adb, connect_device
from app import launch_app
from ui_actions import init_ui_automator, close_cookie_dialog, click_vasita_category, click_otomobil_category
from category_reader import read_vasita_categories
from database import run_migration, save_categories, assign_category_to_device


class SahibindenBot:
    """Sahibinden uygulaması için otomasyon sınıfı"""
    
    def __init__(self):
        """Bot'u başlatır ve ADB bağlantısını kontrol eder"""
        self.device_id = None
        self.d = None  # uiautomator2 device instance
        self.device_token = None
        self.assigned_category = None
        
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
    
    def click_otomobil_category(self):
        """Otomobil kategorisine tıklar"""
        return click_otomobil_category(self.d)

    def run(self):
        """Ana çalıştırma fonksiyonu"""
        print("=" * 50)
        print("Sahibinden Mobilden Otomasyonu")
        print("=" * 50)
        
        # Veritabanı migration
        print("\n--- Veritabanı Hazırlanıyor ---")
        if not run_migration():
            print("⚠️  Veritabanı migration başarısız, devam ediliyor...")
        
        # Ortam değişkeninden cihaz belirtecini al
        self.device_token = os.environ.get("DEVICE_TOKEN")
        if not self.device_token:
            print("✗ DEVICE_TOKEN ortam değişkeni bulunamadı. Lütfen ayarlayıp tekrar deneyin.")
            return False
        print(f"Kullanılacak cihaz belirteci: {self.device_token}")
        
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
        
        # Kategorileri veritabanına kaydet (deviceId boş olacak)
        print("\n--- Kategoriler Veritabanına Kaydediliyor ---")
        if not save_categories(categories, device_id=None, page=1):
            print("⚠️  Kategoriler kaydedilemedi")
            return False
        
        # İşlenecek kategoriyi belirle
        self.assigned_category = assign_category_to_device(self.device_token)
        if not self.assigned_category:
            print("✗ İşlenebilecek kategori bulunamadı.")
            return False
        print(
            "İşlenecek kategori: "
            f"{self.assigned_category['parentCategory']} -> {self.assigned_category['subCategory']} "
            f"(order={self.assigned_category['order']})"
        )

        print("\n" + "=" * 50)
        print("✓ İşlem tamamlandı!")
        print("=" * 50)
        return True

