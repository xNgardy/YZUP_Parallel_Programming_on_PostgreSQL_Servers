#!/usr/bin/env python3
import psycopg2
from faker import Faker
import threading
import time

fake = Faker('tr_TR')

def generate_data_to_server_b():
    server_b_ip = "10.0.2.15"
    
    connection_params = {
        'host': server_b_ip,
        'database': 'testdb',
        'user': 'pgtest',
        'password': 'pgtest123'
    }
    
    print("Server B'ye veri yükleme başlıyor...")
    
    try:
        conn = psycopg2.connect(**connection_params)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        print("Server B bağlantısı başarılı")
    except Exception as e:
        print(f"Server B bağlantı hatası: {e}")
        return
    

    start_time = time.time()
    
    for batch in range(10000):
        try:
            conn = psycopg2.connect(**connection_params)
            cur = conn.cursor()
            
            data = []
            for i in range(1000):
                name = fake.first_name()
                surname = fake.last_name()
                eposta = f"{name.lower()}.{surname.lower()}.{batch}.{i}@{fake.domain_name()}"
                dogum_tarihi = fake.date_between(start_date='-80y', end_date='-18y')
                data.append((name, surname, eposta, dogum_tarihi))
            
            cur.executemany(
                "INSERT INTO kullanicilar (name, surname, eposta, dogum_tarihi) VALUES (%s, %s, %s, %s)",
                data
            )
            
            conn.commit()
            cur.close()
            conn.close()
            
            if batch % 500 == 0:
                print(f"Server B - Batch {batch}/10000 tamamlandı ({batch * 1000:,} kayıt)")
                
        except Exception as e:
            print(f"Hata batch {batch}: {e}")
    
    end_time = time.time()
    print(f"Server B veri yükleme tamamlandı! Süre: {end_time - start_time:.2f} saniye")
    
    try:
        conn = psycopg2.connect(**connection_params)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM kullanicilar")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        print(f"Server B toplam kayıt: {count:,}")
    except Exception as e:
        print(f"Kayıt kontrolü hatası: {e}")

if __name__ == "__main__":
    generate_data_to_server_b()
