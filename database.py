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
            deviceId VARCHAR(255),
            isCompleted BOOLEAN DEFAULT FALSE,
            "order" INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(parentCategory, subCategory, deviceId)
        );
        """
        
        cursor.execute(create_table_query)
        
        # Eğer tablo zaten varsa, order kolonunu ekle (migration)
        try:
            cursor.execute("""
                ALTER TABLE categories 
                ADD COLUMN IF NOT EXISTS "order" INTEGER DEFAULT 1;
            """)
        except Exception as e:
            # Kolon zaten varsa hata vermez, devam et
            pass
        
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
    """Kategori kaydının var olup olmadığını kontrol eder (deviceId NULL olabilir)"""
    try:
        cursor = conn.cursor()
        # deviceId NULL ise veya boş string ise, NULL olarak kontrol et
        if not device_id or device_id.strip() == '':
            cursor.execute(
                "SELECT id FROM categories WHERE parentCategory = %s AND subCategory = %s AND (deviceId IS NULL OR deviceId = '')",
                (parent_category, sub_category)
            )
        else:
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


def insert_category(conn, parent_category, sub_category, page, device_id, is_completed=False, order=1):
    """Yeni kategori kaydı ekler"""
    try:
        cursor = conn.cursor()
        # deviceId boş string ise NULL yap
        device_id_value = None if (not device_id or device_id.strip() == '') else device_id
        
        cursor.execute(
            """
            INSERT INTO categories (parentCategory, subCategory, page, deviceId, isCompleted, "order")
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (parentCategory, subCategory, deviceId) 
            DO UPDATE SET 
                page = EXCLUDED.page,
                isCompleted = EXCLUDED.isCompleted,
                "order" = EXCLUDED."order",
                updated_at = CURRENT_TIMESTAMP
            """,
            (parent_category, sub_category, page, device_id_value, is_completed, order)
        )
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"✗ Kategori ekleme sırasında hata: {e}")
        conn.rollback()
        return False


def has_any_categories():
    """Tabloda herhangi bir kategori olup olmadığını kontrol eder."""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT EXISTS (SELECT 1 FROM categories LIMIT 1);")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return bool(result[0]) if result else False
    except Exception as e:
        print(f"✗ Kategori varlık kontrolü sırasında hata: {e}")
        if conn:
            conn.close()
        return False


def save_categories(categories, device_id=None, page=1):
    """Kategori listesini veritabanına kaydeder (öncelikli kategoriler önce işlenir)"""
    from category_reader import is_priority_category
    
    conn = get_db_connection()
    if not conn:
        return False
    
    parent_category = "Vasıta"
    # deviceId boş olacak (ileride kullanılacak)
    device_id = ""  # Boş string, NULL olarak kaydedilecek
    
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
        # Önce öncelikli kategorileri işle (order = 0)
        for sub_category in priority_categories:
            if not category_exists(conn, parent_category, sub_category, device_id):
                if insert_category(conn, parent_category, sub_category, page, device_id, is_completed=False, order=0):
                    priority_new += 1
                    print(f"  ✓ [ÖNCELİKLİ] Yeni kategori kaydedildi: {sub_category} (order=0)")
                else:
                    print(f"  ✗ [ÖNCELİKLİ] Kategori kaydedilemedi: {sub_category}")
            else:
                priority_existing += 1
                print(f"  ⊙ [ÖNCELİKLİ] Kategori zaten mevcut: {sub_category}")
        
        # Sonra diğer kategorileri işle (order = 1)
        if other_categories:
            print(f"\n--- Diğer Kategoriler Kaydediliyor ({len(other_categories)} adet) ---")
            for sub_category in other_categories:
                if not category_exists(conn, parent_category, sub_category, device_id):
                    if insert_category(conn, parent_category, sub_category, page, device_id, is_completed=False, order=1):
                        other_new += 1
                        print(f"  ✓ Yeni kategori kaydedildi: {sub_category} (order=1)")
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


def _map_category_row(row):
    """Helper to convert a category row tuple into a dict."""
    return {
        "id": row[0],
        "parentCategory": row[1],
        "subCategory": row[2],
        "page": row[3],
        "deviceId": row[4],
        "isCompleted": row[5],
        "order": row[6],
    }


def assign_category_to_device(device_token):
    """Assigns or retrieves a category for the provided device token."""
    if not device_token:
        print("✗ Geçersiz cihaz belirteci.")
        return None
    
    conn = get_db_connection()
    if not conn:
        return None
    
    cursor = None
    assigned = None
    
    try:
        cursor = conn.cursor()
        
        # Step 1: Try to find an unfinished category already assigned to this device
        cursor.execute(
            """
            SELECT id, parentCategory, subCategory, page, deviceId, isCompleted, "order"
            FROM categories
            WHERE isCompleted = FALSE AND deviceId = %s
            ORDER BY "order" ASC, id ASC
            LIMIT 1
            """,
            (device_token,)
        )
        row = cursor.fetchone()
        if row:
            assigned = _map_category_row(row)
            return assigned
        
        # Step 2: Claim a pending priority category (order = 0)
        cursor.execute(
            """
            WITH selected AS (
                SELECT id FROM categories
                WHERE isCompleted = FALSE
                  AND "order" = 0
                  AND (deviceId IS NULL OR deviceId = '')
                ORDER BY id
                LIMIT 1
            )
            UPDATE categories AS c
            SET deviceId = %s, updated_at = CURRENT_TIMESTAMP
            FROM selected
            WHERE c.id = selected.id
            RETURNING c.id, c.parentCategory, c.subCategory, c.page, c.deviceId, c.isCompleted, c."order"
            """,
            (device_token,)
        )
        row = cursor.fetchone()
        if row:
            conn.commit()
            assigned = _map_category_row(row)
            return assigned
        
        # Step 3: Claim a pending non-priority category (order = 1)
        cursor.execute(
            """
            WITH selected AS (
                SELECT id FROM categories
                WHERE isCompleted = FALSE
                  AND "order" = 1
                  AND (deviceId IS NULL OR deviceId = '')
                ORDER BY id
                LIMIT 1
            )
            UPDATE categories AS c
            SET deviceId = %s, updated_at = CURRENT_TIMESTAMP
            FROM selected
            WHERE c.id = selected.id
            RETURNING c.id, c.parentCategory, c.subCategory, c.page, c.deviceId, c.isCompleted, c."order"
            """,
            (device_token,)
        )
        row = cursor.fetchone()
        if row:
            conn.commit()
            assigned = _map_category_row(row)
            return assigned
        
        return None
    
    except Exception as e:
        print(f"✗ Kategori seçimi sırasında hata: {e}")
        if conn:
            conn.rollback()
        return None
    
    finally:
        if cursor:
            cursor.close()
        conn.close()

