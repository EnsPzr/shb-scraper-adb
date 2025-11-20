#!/usr/bin/env python3
"""
Uygulama yönetimi modülü
"""

import subprocess
import time


# Sahibinden uygulamasının paket adı
SAHIBINDEN_PACKAGE = "com.sahibinden"


def is_app_installed(device_id):
    """Sahibinden uygulamasının kurulu olup olmadığını kontrol eder"""
    try:
        cmd = ['adb']
        if device_id:
            cmd.extend(['-s', device_id])
        cmd.extend(['shell', 'pm', 'list', 'packages', SAHIBINDEN_PACKAGE])

        result = subprocess.run(cmd, 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        
        is_installed = SAHIBINDEN_PACKAGE in result.stdout
        
        if is_installed:
            print(f"✓ Sahibinden uygulaması kurulu")
        else:
            print(f"✗ Sahibinden uygulaması bulunamadı (paket: {SAHIBINDEN_PACKAGE})")
            
        return is_installed
    except Exception as e:
        print(f"✗ Uygulama kontrolü sırasında hata: {e}")
        return False


def is_app_running(device_id):
    """Sahibinden uygulamasının çalışıp çalışmadığını kontrol eder"""
    try:
        cmd = ['adb']
        if device_id:
            cmd.extend(['-s', device_id])
        cmd.extend(['shell', 'pidof', SAHIBINDEN_PACKAGE])
        
        result = subprocess.run(cmd, 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        
        # Eğer pidof bir PID döndürürse, uygulama çalışıyor demektir
        is_running = result.stdout.strip() != ''
        return is_running
    except Exception as e:
        # Hata durumunda False döndür (güvenli taraf)
        return False


def launch_app(device_id):
    """Sahibinden uygulamasını açar (eğer çalışıyorsa önce kapatır)"""
    print("\n--- Uygulama Başlatılıyor ---")
    
    if not is_app_installed(device_id):
        print("✗ Uygulama kurulu olmadığı için başlatılamıyor")
        return False
    
    try:
        # Önce uygulamanın çalışıp çalışmadığını kontrol et
        if is_app_running(device_id):
            print("  → Uygulama çalışıyor, kapatılıyor...")
            cmd_stop = ['adb']
            if device_id:
                cmd_stop.extend(['-s', device_id])
            cmd_stop.extend(['shell', 'am', 'force-stop', SAHIBINDEN_PACKAGE])
            subprocess.run(cmd_stop, capture_output=True, timeout=5)
            time.sleep(1)  # Kapanma için kısa bekleme
            print("  ✓ Uygulama kapatıldı")
        else:
            print("  → Uygulama çalışmıyor, direkt başlatılıyor...")
        
        # Uygulamayı durdur (eğer hala çalışıyorsa)
        cmd_stop = ['adb']
        if device_id:
            cmd_stop.extend(['-s', device_id])
        cmd_stop.extend(['shell', 'am', 'force-stop', SAHIBINDEN_PACKAGE])
        subprocess.run(cmd_stop, capture_output=True, timeout=5)
        time.sleep(0.5)  # Kapanma için kısa bekleme
        
        # Monkey komutu ile uygulamayı başlat (en güvenli yöntem)
        # Bu yöntem, exported olmayan aktiviteleri de başlatabilir
        cmd_start = ['adb']
        if device_id:
            cmd_start.extend(['-s', device_id])
        cmd_start.extend([
            'shell', 'monkey', 
            '-p', SAHIBINDEN_PACKAGE,
            '-c', 'android.intent.category.LAUNCHER',
            '1'
        ])
        
        result = subprocess.run(cmd_start, 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        
        if result.returncode == 0 and 'Events injected' in result.stdout:
            print(f"✓ Sahibinden uygulaması başlatıldı")
            print(f"  Paket: {SAHIBINDEN_PACKAGE}")
            time.sleep(2)  # Uygulamanın açılması için bekle
            return True
        else:
            print(f"✗ Uygulama başlatılırken hata:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ Uygulama başlatma sırasında hata: {e}")
        return False

