#!/usr/bin/env python3
"""
Sahibinden Mobilden Otomasyonu
Bu script ADB kullanarak Android cihaza bağlanır ve Sahibinden uygulamasını açar.
"""

import subprocess
import time
import sys
import uiautomator2 as u2


class SahibindenBot:
    """Sahibinden uygulaması için otomasyon sınıfı"""
    
    # Sahibinden uygulamasının paket adı
    SAHIBINDEN_PACKAGE = "com.sahibinden"
    # Ana activity: BrowsingFeaturedClassifiedsActivity (ana ilan listesi sayfası)
    SAHIBINDEN_ACTIVITY = "com.sahibinden.ui.browsing.BrowsingFeaturedClassifiedsActivity"
    def __init__(self):
        """Bot'u başlatır ve ADB bağlantısını kontrol eder"""
        self.device_id = None
        self.d = None  # uiautomator2 device instance
        
    def check_adb(self):
        """ADB'nin kurulu olup olmadığını kontrol eder"""
        try:
            result = subprocess.run(['adb', 'version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                print("✓ ADB başarıyla bulundu")
                print(result.stdout.split('\n')[0])
                return True
            else:
                print("✗ ADB bulunamadı. Lütfen Android SDK Platform-Tools'u yükleyin.")
                print("\nKurulum için:")
                print("  macOS: brew install android-platform-tools")
                print("  veya: https://developer.android.com/tools/releases/platform-tools")
                return False
        except FileNotFoundError:
            print("✗ ADB bulunamadı. Lütfen Android SDK Platform-Tools'u yükleyin.")
            print("\nKurulum için:")
            print("  macOS: brew install android-platform-tools")
            return False
        except Exception as e:
            print(f"✗ ADB kontrolü sırasında hata: {e}")
            return False
    
    def get_connected_devices(self):
        """Bağlı cihazları listeler"""
        try:
            result = subprocess.run(['adb', 'devices'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            lines = result.stdout.strip().split('\n')[1:]  # İlk satırı atla (başlık)
            print(lines)
            devices = []
            for line in lines:
                if line.strip() and '\tdevice' in line:
                    device_id = line.split('\t')[0]
                    devices.append(device_id)
            print(devices)
            return devices
        except Exception as e:
            print(f"✗ Cihaz listesi alınırken hata: {e}")
            return []
    
    def connect_device(self):
        """Cihaza bağlanır"""
        print("\n--- Cihaz Bağlantısı ---")
        
        devices = self.get_connected_devices()
        
        if not devices:
            print("✗ Bağlı cihaz bulunamadı!")
            print("\nLütfen:")
            print("  1. Cihazınızı USB ile bağlayın")
            print("  2. USB hata ayıklama (USB debugging) açık olduğundan emin olun")
            print("  3. Bilgisayarı güvenilir cihaz olarak onaylayın")
            return False
        
        if len(devices) == 1:
            self.device_id = devices[0]
            print(f"✓ Cihaza bağlanıldı: {self.device_id}")
            return True
        else:
            print(f"✓ {len(devices)} cihaz bulundu:")
            for i, device in enumerate(devices, 1):
                print(f"  {i}. {device}")
            self.device_id = devices[0]
            print(f"✓ İlk cihaz seçildi: {self.device_id}")
            return True
    
    def is_app_installed(self):
        """Sahibinden uygulamasının kurulu olup olmadığını kontrol eder"""
        try:
            cmd = ['adb']
            if self.device_id:
                cmd.extend(['-s', self.device_id])
            cmd.extend(['shell', 'pm', 'list', 'packages', self.SAHIBINDEN_PACKAGE])

            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            
            is_installed = self.SAHIBINDEN_PACKAGE in result.stdout
            
            if is_installed:
                print(f"✓ Sahibinden uygulaması kurulu")
            else:
                print(f"✗ Sahibinden uygulaması bulunamadı (paket: {self.SAHIBINDEN_PACKAGE})")
                
            return is_installed
        except Exception as e:
            print(f"✗ Uygulama kontrolü sırasında hata: {e}")
            return False
    
    def launch_app(self):
        """Sahibinden uygulamasını açar"""
        print("\n--- Uygulama Başlatılıyor ---")
        
        if not self.is_app_installed():
            print("✗ Uygulama kurulu olmadığı için başlatılamıyor")
            return False
        
        try:
            # Önce uygulamayı durdur (temiz başlangıç için)
            cmd_stop = ['adb']
            if self.device_id:
                cmd_stop.extend(['-s', self.device_id])
            cmd_stop.extend(['shell', 'am', 'force-stop', self.SAHIBINDEN_PACKAGE])
            subprocess.run(cmd_stop, capture_output=True, timeout=5)
            
            # Monkey komutu ile uygulamayı başlat (en güvenli yöntem)
            # Bu yöntem, exported olmayan aktiviteleri de başlatabilir
            cmd_start = ['adb']
            if self.device_id:
                cmd_start.extend(['-s', self.device_id])
            cmd_start.extend([
                'shell', 'monkey', 
                '-p', self.SAHIBINDEN_PACKAGE,
                '-c', 'android.intent.category.LAUNCHER',
                '1'
            ])
            
            result = subprocess.run(cmd_start, 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            
            if result.returncode == 0 and 'Events injected' in result.stdout:
                print(f"✓ Sahibinden uygulaması başlatıldı")
                print(f"  Paket: {self.SAHIBINDEN_PACKAGE}")
                time.sleep(2)  # Uygulamanın açılması için bekle
                return True
            else:
                print(f"✗ Uygulama başlatılırken hata:")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"✗ Uygulama başlatma sırasında hata: {e}")
            return False
    
    def init_ui_automator(self):
        """UIAutomator2 bağlantısını başlatır"""
        try:
            print("\n--- UI Otomasyon Hazırlanıyor ---")
            self.d = u2.connect(self.device_id)
            print(f"✓ UI otomasyon bağlantısı kuruldu")
            return True
        except Exception as e:
            print(f"✗ UI otomasyon bağlantısı kurulamadı: {e}")
            return False
    
    def close_cookie_dialog(self):
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
                if self.d(text=button_text).exists(timeout=2):
                    print(f"✓ '{button_text}' butonu bulundu, tıklanıyor...")
                    self.d(text=button_text).click()
                    time.sleep(1)
                    print(f"✓ Çerez dialogu kapatıldı")
                    return True
            
            # textContains ile dene (kısmi eşleşme)
            if self.d(textContains="Reddet").exists(timeout=2):
                print(f"✓ 'Reddet' içeren buton bulundu, tıklanıyor...")
                self.d(textContains="Reddet").click()
                time.sleep(1)
                print(f"✓ Çerez dialogu kapatıldı")
                return True
            
            # Resource ID ile de dene
            if self.d(resourceId="com.sahibinden:id/rejectButton").exists(timeout=2):
                print(f"✓ Reddet butonu (ID ile) bulundu, tıklanıyor...")
                self.d(resourceId="com.sahibinden:id/rejectButton").click()
                time.sleep(1)
                print(f"✓ Çerez dialogu kapatıldı")
                return True
            
            if self.d(resourceId="com.sahibinden:id/acceptButton").exists(timeout=2):
                print(f"✓ Kabul butonu (ID ile) bulundu, tıklanıyor...")
                self.d(resourceId="com.sahibinden:id/acceptButton").click()
                time.sleep(1)
                print(f"✓ Çerez dialogu kapatıldı")
                return True
            
            print("⚠️  Çerez dialogu bulunamadı (zaten kapalı olabilir)")
            return True
            
        except Exception as e:
            print(f"⚠️  Çerez dialogu kapatılırken hata: {e}")
            # Hata olsa bile devam et
            return True
    
    def click_vasita_category(self):
        """Vasıta kategorisine tıklar"""
        print("\n--- Vasıta Kategorisine Tıklanıyor ---")
        try:
            # Çeşitli olası yolları dene
            
            # 1. Text ile arama
            if self.d(text="Vasıta").exists(timeout=3):
                print(f"✓ 'Vasıta' kategorisi bulundu (text ile)")
                self.d(text="Vasıta").click()
                time.sleep(2)
                print(f"✓ Vasıta kategorisine tıklandı")
                return True
            
            # 2. VASITA (büyük harf)
            if self.d(text="VASITA").exists(timeout=3):
                print(f"✓ 'VASITA' kategorisi bulundu")
                self.d(text="VASITA").click()
                time.sleep(2)
                print(f"✓ Vasıta kategorisine tıklandı")
                return True
            
            # 3. textContains ile
            if self.d(textContains="Vasıta").exists(timeout=3):
                print(f"✓ Vasıta içeren kategori bulundu")
                self.d(textContains="Vasıta").click()
                time.sleep(2)
                print(f"✓ Vasıta kategorisine tıklandı")
                return True
            
            # 4. description ile
            if self.d(description="Vasıta").exists(timeout=3):
                print(f"✓ Vasıta kategorisi bulundu (description ile)")
                self.d(description="Vasıta").click()
                time.sleep(2)
                print(f"✓ Vasıta kategorisine tıklandı")
                return True
            
            print("✗ Vasıta kategorisi bulunamadı")
            print("💡 Ekran XML'ini kontrol edebilirsiniz: adb shell uiautomator dump")
            return False
            
        except Exception as e:
            print(f"✗ Vasıta kategorisine tıklanırken hata: {e}")
            return False
    
    def run(self):
        """Ana çalıştırma fonksiyonu"""
        print("=" * 50)
        print("Sahibinden Mobilden Otomasyonu")
        print("=" * 50)
        
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
        if not self.close_cookie_dialog():
            print("⚠️  Çerez dialogu kapatılamadı ama devam ediliyor...")
        
        # Vasıta kategorisine tıkla
        if not self.click_vasita_category():
            return False
        
        print("\n" + "=" * 50)
        print("✓ İşlem tamamlandı!")
        print("=" * 50)
        return True


def main():
    """Ana giriş noktası"""
    bot = SahibindenBot()
    success = bot.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

