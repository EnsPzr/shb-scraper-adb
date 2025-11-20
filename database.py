#!/usr/bin/env python3
"""
PostgreSQL veritabanı bağlantı ve migration modülü
"""

import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()


def get_db_connection():
    """PostgreSQL veritabanı bağlantısı oluşturur"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', '45.147.47.18'),
            port=os.getenv('DB_PORT', '6432'),
            database=os.getenv('DB_NAME', 'instant-cash'),
            user=os.getenv('DB_USER', 'instant-cash'),
            password=os.getenv('DB_PASSWORD', 'E3PsdnJ71n5J2If7sI11Rg9z')
        )
        return conn
    except Exception as e:
        print(f"✗ Veritabanı bağlantısı kurulamadı: {e}")
        return None


def run_migration():
    """Veritabanı tablosunu oluşturur (migration)"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Tablo oluştur
        create_table_query = """
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            parentCategory VARCHAR(255) NOT NULL,
            subCategory VARCHAR(255) NOT NULL,
            page INTEGER DEFAULT 1,
            deviceId VARCHAR(255) NOT NULL,
            isCompleted BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(parentCategory, subCategory, deviceId)
        );
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✓ Veritabanı tablosu oluşturuldu/kontrol edildi")
        return True
        
    except Exception as e:
        print(f"✗ Migration sırasında hata: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False


def category_exists(conn, parent_category, sub_category, device_id):
    """Kategori kaydının var olup olmadığını kontrol eder"""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM categories WHERE parentCategory = %s AND subCategory = %s AND deviceId = %s",
            (parent_category, sub_category, device_id)
        )
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    except Exception as e:
        print(f"✗ Kategori kontrolü sırasında hata: {e}")
        return False


def insert_category(conn, parent_category, sub_category, page, device_id, is_completed=False):
    """Yeni kategori kaydı ekler"""
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO categories (parentCategory, subCategory, page, deviceId, isCompleted)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (parentCategory, subCategory, deviceId) 
            DO UPDATE SET 
                page = EXCLUDED.page,
                isCompleted = EXCLUDED.isCompleted,
                updated_at = CURRENT_TIMESTAMP
            """,
            (parent_category, sub_category, page, device_id, is_completed)
        )
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"✗ Kategori ekleme sırasında hata: {e}")
        conn.rollback()
        return False


def save_categories(categories, device_id, page=1):
    """Kategori listesini veritabanına kaydeder (öncelikli kategoriler önce işlenir)"""
    from category_reader import is_priority_category
    
    conn = get_db_connection()
    if not conn:
        return False
    
    parent_category = "Vasıta"
    
    # Kategorileri öncelikli ve diğerleri olarak ayır
    priority_categories = [cat for cat in categories if is_priority_category(cat)]
    other_categories = [cat for cat in categories if not is_priority_category(cat)]
    
    # Sayıcılar
    priority_new = 0
    priority_existing = 0
    other_new = 0
    other_existing = 0
    
    print(f"\n--- Öncelikli Kategoriler Kaydediliyor ({len(priority_categories)} adet) ---")
    
    try:
        # Önce öncelikli kategorileri işle
        for sub_category in priority_categories:
            if not category_exists(conn, parent_category, sub_category, device_id):
                if insert_category(conn, parent_category, sub_category, page, device_id):
                    priority_new += 1
                    print(f"  ✓ [ÖNCELİKLİ] Yeni kategori kaydedildi: {sub_category}")
                else:
                    print(f"  ✗ [ÖNCELİKLİ] Kategori kaydedilemedi: {sub_category}")
            else:
                priority_existing += 1
                print(f"  ⊙ [ÖNCELİKLİ] Kategori zaten mevcut: {sub_category}")
        
        # Sonra diğer kategorileri işle
        if other_categories:
            print(f"\n--- Diğer Kategoriler Kaydediliyor ({len(other_categories)} adet) ---")
            for sub_category in other_categories:
                if not category_exists(conn, parent_category, sub_category, device_id):
                    if insert_category(conn, parent_category, sub_category, page, device_id):
                        other_new += 1
                        print(f"  ✓ Yeni kategori kaydedildi: {sub_category}")
                    else:
                        print(f"  ✗ Kategori kaydedilemedi: {sub_category}")
                else:
                    other_existing += 1
                    print(f"  ⊙ Kategori zaten mevcut: {sub_category}")
        
        conn.close()
        total_new = priority_new + other_new
        total_existing = priority_existing + other_existing
        print(f"\n✓ Toplam {len(categories)} kategori işlendi:")
        print(f"  - Öncelikli: {len(priority_categories)} ({priority_new} yeni, {priority_existing} mevcut)")
        print(f"  - Diğerleri: {len(other_categories)} ({other_new} yeni, {other_existing} mevcut)")
        print(f"  - Toplam: {total_new} yeni, {total_existing} mevcut")
        return True
        
    except Exception as e:
        print(f"✗ Kategori kaydetme sırasında hata: {e}")
        if conn:
            conn.close()
        return False

