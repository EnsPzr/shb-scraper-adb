#!/usr/bin/env python3
"""
Cihaz ve ADB yönetimi modülü
"""

import subprocess


def check_adb():
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


def get_connected_devices():
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


def connect_device():
    """Cihaza bağlanır"""
    print("\n--- Cihaz Bağlantısı ---")
    
    devices = get_connected_devices()
    
    if not devices:
        print("✗ Bağlı cihaz bulunamadı!")
        print("\nLütfen:")
        print("  1. Cihazınızı USB ile bağlayın")
        print("  2. USB hata ayıklama (USB debugging) açık olduğundan emin olun")
        print("  3. Bilgisayarı güvenilir cihaz olarak onaylayın")
        return None
    
    if len(devices) == 1:
        device_id = devices[0]
        print(f"✓ Cihaza bağlanıldı: {device_id}")
        return device_id
    else:
        print(f"✓ {len(devices)} cihaz bulundu:")
        for i, device in enumerate(devices, 1):
            print(f"  {i}. {device}")
        device_id = devices[0]
        print(f"✓ İlk cihaz seçildi: {device_id}")
        return device_id

