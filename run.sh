#!/bin/bash

# Virtual environment klasör yolu
VENV_DIR="path/to/venv"

# Virtual environment var mı kontrol et
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment oluşturuluyor..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Hata: Virtual environment oluşturulamadı!"
        exit 1
    fi
    echo "Virtual environment başarıyla oluşturuldu."
fi

# Virtual environment'ı aktifleştir
echo "Virtual environment aktifleştiriliyor..."
source "$VENV_DIR/bin/activate"

# Paketleri yükle
echo "Gerekli paketler yükleniyor..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Hata: Paketler yüklenemedi!"
    deactivate
    exit 1
fi

echo "Paketler başarıyla yüklendi."
echo "Sahibinden bot başlatılıyor..."
echo "----------------------------------------"

# Python botunu çalıştır
python3 sahibinden_bot.py

# Çıkış kodunu kaydet
EXIT_CODE=$?

# Virtual environment'ı kapat
deactivate

# Programın çıkış koduyla çık
exit $EXIT_CODE

