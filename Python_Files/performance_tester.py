#!/usr/bin/env python3
import psycopg2
import time
import json
from datetime import datetime

class PerformanceTester:
    def __init__(self, host, server_name):
        self.connection_params = {
            'host': host,
            'database': 'testdb',
            'user': 'pgtest',
            'password': 'pgtest123'
        }
        self.server_name = server_name
        self.results = []
    
    def execute_query(self, query, description, params=None):
        try:
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            
            start_time = time.perf_counter()
            
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
                
            results = cur.fetchall()
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            
            result = {
                'server': self.server_name,
                'query': description,
                'execution_time': execution_time,
                'row_count': len(results),
                'timestamp': datetime.now().isoformat()
            }
            
            self.results.append(result)
            cur.close()
            conn.close()
            
            print(f"{self.server_name} - {description}: {execution_time:.3f}s ({len(results)} satir)")
            return result
            
        except Exception as e:
            print(f"HATA - {self.server_name} - {description}: {e}")
            return None
    
    def run_tests(self):
        print(f"\n=== {self.server_name} Performans Testleri ===")
        
        self.execute_query(
            "SELECT * FROM kullanicilar WHERE id = %s;", 
            "Belirli bir kullaniciyi id ile getirme", 
            (500000,)
        )
        
        self.execute_query(
            "SELECT * FROM kullanicilar WHERE eposta LIKE %s LIMIT 1000;", 
            "Belirli bir eposta ile arama", 
            ('%gmail.com%',)
        )
        
        self.execute_query(
            "SELECT * FROM kullanicilar WHERE dogum_tarihi BETWEEN %s AND %s LIMIT 5000;", 
            "dogum_tarihi araliginda filtreleme", 
            ('1990-01-01', '2000-01-01')
        )
        
        self.execute_query(
            "SELECT surname, COUNT(*) as count FROM kullanicilar GROUP BY surname ORDER BY count DESC LIMIT 100;", 
            "surname'e gore gruplama ve siralama", 
            None
        )
        
        print(f"{self.server_name} testleri tamamlandi")
    
    def save_results(self):
        filename = f'performance_results_{self.server_name.lower().replace(" ", "_")}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"Sonuclar kaydedildi: {filename}")

def main():
    print("PostgreSQL Performans Testleri")
    print("=" * 50)
    print("Test sirasi: Server B (Hatali) -> Server A (Optimum)")
    print("=" * 50)
    
    print("\nServer B (Hatali Konfigürasyon) Testleri")
    tester_b = PerformanceTester('10.0.2.15', 'Server_B')
    tester_b.run_tests()
    tester_b.save_results()
    
    time.sleep(3)
    
    print("\nServer A (Optimum Konfigürasyon) Testleri")
    tester_a = PerformanceTester('localhost', 'Server_A')
    tester_a.run_tests()
    tester_a.save_results()
    
    print("\nTum performans testleri tamamlandi")
    
    print("\nPerformans Karsilastirmasi:")
    try:
        with open('performance_results_server_a.json', 'r') as f:
            results_a = json.load(f)
        with open('performance_results_server_b.json', 'r') as f:
            results_b = json.load(f)
        
        print("Test                               | Server A (s) | Server B (s) | Iyilestirme")
        print("-" * 75)
        
        for test_a, test_b in zip(results_a, results_b):
            time_a = test_a['execution_time']
            time_b = test_b['execution_time']
            improvement = time_b / time_a if time_a > 0 else 0
            
            test_name = test_a['query'][:30]
            print(f"{test_name:<30} | {time_a:>8.3f}    | {time_b:>8.3f}    | {improvement:>6.2f}x")
        
        avg_a = sum(r['execution_time'] for r in results_a) / len(results_a)
        avg_b = sum(r['execution_time'] for r in results_b) / len(results_b)
        overall = avg_b / avg_a if avg_a > 0 else 0
        
        print("-" * 75)
        print(f"{'ORTALAMA':<30} | {avg_a:>8.3f}    | {avg_b:>8.3f}    | {overall:>6.2f}x")
        
        if overall > 1:
            print(f"\nSonuc: Server A (Optimum), Server B'den {overall:.1f} kat daha hizli")
        else:
            print(f"\nSonuc: Server B, Server A'dan {1/overall:.1f} kat daha hizli")
        
    except Exception as e:
        print(f"Karsilastirma hatasi: {e}")

if __name__ == "__main__":
    main()
