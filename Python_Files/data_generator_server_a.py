#!/usr/bin/env python3
import psycopg2
from faker import Faker
import threading
import time
import sys

fake = Faker('tr_TR')

class DataGenerator:
    def __init__(self, host, database, user, password, server_name):
        self.connection_params = {
            'host': host,
            'database': database,
            'user': user,
            'password': password
        }
        self.server_name = server_name
    
    def test_connection(self):
        try:
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.close()
            conn.close()
            print(f"{self.server_name} bağlantısı başarılı")
            return True
        except Exception as e:
            print(f"{self.server_name} bağlantı hatası: {e}")
            return False
    
    def generate_batch(self, batch_size, batch_number):
        try:
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            
            data = []
            for i in range(batch_size):
                name = fake.first_name()
                surname = fake.last_name()
                eposta = f"{name.lower()}.{surname.lower()}.{batch_number}.{i}@{fake.domain_name()}"
                dogum_tarihi = fake.date_between(start_date='-80y', end_date='-18y')
                
                data.append((name, surname, eposta, dogum_tarihi))
            
            cur.executemany(
                "INSERT INTO kullanicilar (name, surname, eposta, dogum_tarihi) VALUES (%s, %s, %s, %s)",
                data
            )
            
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"{self.server_name} - Batch {batch_number}: {batch_size} kayıt eklendi")
            return True
            
        except Exception as e:
            print(f"HATA - {self.server_name} Batch {batch_number}: {e}")
            return False
    
    def generate_data_threaded(self, total_records=1000000, batch_size=5000, num_threads=4):
        print(f"\n{self.server_name} - {total_records:,} kayıt üretimi başlatılıyor...")
        print(f"Batch boyutu: {batch_size}, Thread sayısı: {num_threads}")
        
        batches_per_thread = (total_records // batch_size) // num_threads
        threads = []
        start_time = time.time()
        
        for thread_id in range(num_threads):
            thread = threading.Thread(
                target=self.generate_batches_for_thread,
                args=(thread_id, batches_per_thread, batch_size)
            )
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        print(f"{self.server_name} - Tamamlandı! Süre: {end_time - start_time:.2f} saniye")
        
        self.check_record_count()
    
    def generate_batches_for_thread(self, thread_id, num_batches, batch_size):
        for batch_num in range(num_batches):
            batch_number = (thread_id * num_batches) + batch_num
            self.generate_batch(batch_size, batch_number)
    
    def check_record_count(self):
        try:
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM kullanicilar")
            count = cur.fetchone()[0]
            cur.close()
            conn.close()
            print(f"{self.server_name} - Toplam kayıt sayısı: {count:,}")
        except Exception as e:
            print(f"Kayıt sayısı kontrolü hatası: {e}")

def main():
    print("PostgreSQL Veri Üretici")
    print("=" * 50)
    
    servers = [
        {
            'host': 'localhost', 
            'name': 'Server A (Optimum)'
        }

    ]
    
    generators = []
    
    for server in servers:
        generator = DataGenerator(
            host=server['host'],
            database='testdb',
            user='pgtest',
            password='pgtest123',
            server_name=server['name']
        )
        
        if generator.test_connection():
            generators.append(generator)
        else:
            print(f"{server['name']} atlanıyor...")
    
    if not generators:
        print("Hiçbir sunucuya bağlanılamadı!")
        return
    
    print(f"\n{len(generators)} sunucuya veri üretimi başlatılıyor...")
    
    record_count = 10000000
    
    for generator in generators:
        print(f"\n{'='*60}")
        generator.generate_data_threaded(
            total_records=record_count,
            batch_size=5000,
            num_threads=4
        )
    
    print(f"\nTÜM SUNUCULARA VERİ ÜRETİMİ TAMAMLANDI!")
    print("=" * 60)

if __name__ == "__main__":
    main()
