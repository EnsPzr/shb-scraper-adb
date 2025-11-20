# Sahibinden Mobilden Otomasyonu

Bu proje, ADB kullanarak Android cihazlarda Sahibinden uygulamasını otomatik olarak kontrol etmek için geliştirilmiştir.

## Gereksinimler

### 1. ADB (Android Debug Bridge)
macOS üzerinde kurulum:
```bash
brew install android-platform-tools
```

### 2. Python Paketleri
```bash
pip install -r requirements.txt
```

## Kullanım

### Temel Kullanım
```bash
python sahibinden_bot.py
```

## Özellikler

- ✅ ADB kontrolü ve cihaz bağlantısı
- ✅ Sahibinden uygulamasını otomatik açma
- ⏳ İlan arama (yakında)
- ⏳ Bildirim gönderme (yakında)

## Kurulum Adımları

1. **ADB Kurulumu:**
   ```bash
   brew install android-platform-tools
   ```

2. **Python Bağımlılıkları:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Android Cihaz Hazırlığı:**
   - USB hata ayıklama (USB debugging) aktif edilmeli
   - Cihaz USB ile bağlanmalı
   - Bilgisayar güvenilir cihaz olarak onaylanmalı

4. **Çalıştır:**
   ```bash
   python sahibinden_bot.py
   ```

## Notlar

- Cihazınızda "USB hata ayıklama" (Developer Options > USB Debugging) açık olmalı
- İlk bağlantıda cihazınızda güvenlik onayı isteyecektir
- Sahibinden uygulaması cihazda kurulu olmalıdır (paket: `com.asusnova.sahibinden`)

