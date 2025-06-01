#!/usr/bin/env python3
import psycopg2
import asyncpg
import asyncio
import threading
import concurrent.futures
import time
import json
from datetime import datetime

class ParallelTester:
    def __init__(self, host, server_name):
        self.connection_params = {
            'host': host,
            'database': 'testdb',
            'user': 'pgtest',
            'password': 'pgtest123'
        }
        self.server_name = server_name
        self.results = []
    
    def single_query(self, user_id):
        try:
            conn = psycopg2.connect(**self.connection_params)
            cur = conn.cursor()
            
            start_time = time.perf_counter()
            cur.execute("SELECT * FROM kullanicilar WHERE id = %s", (user_id,))
            result = cur.fetchone()
            end_time = time.perf_counter()
            
            cur.close()
            conn.close()
            
            return end_time - start_time, result
        except Exception as e:
            print(f"Sorgu hatasi (ID: {user_id}): {e}")
            return 0, None
    
    def sequential_test(self, user_ids):
        print(f"\n{self.server_name} - Sirali Test")
        print("-" * 40)
        
        start_time = time.perf_counter()
        individual_times = []
        
        for i, user_id in enumerate(user_ids):
            exec_time, result = self.single_query(user_id)
            individual_times.append(exec_time)
            print(f"Sorgu {i+1:2d}/10: {exec_time:.3f}s (ID: {user_id})")
        
        total_time = time.perf_counter() - start_time
        avg_time = sum(individual_times) / len(individual_times)
        
        result_data = {
            'server': self.server_name,
            'test_type': 'Sirali',
            'total_time': total_time,
            'avg_query_time': avg_time,
            'query_count': len(user_ids),
            'individual_times': individual_times
        }
        
        self.results.append(result_data)
        print(f"Sirali test toplam suresi: {total_time:.3f}s")
        return result_data
    
    def parallel_threading_test(self, user_ids, max_workers=5):
        print(f"\n{self.server_name} - Paralel Test (Threading)")
        print("-" * 40)
        
        start_time = time.perf_counter()
        individual_times = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_id = {executor.submit(self.single_query, user_id): user_id for user_id in user_ids}
            
            completed = 0
            for future in concurrent.futures.as_completed(future_to_id):
                user_id = future_to_id[future]
                completed += 1
                try:
                    exec_time, result = future.result()
                    individual_times.append(exec_time)
                    print(f"Thread {completed:2d}/10: {exec_time:.3f}s (ID: {user_id})")
                except Exception as exc:
                    print(f"Thread hatasi (ID: {user_id}): {exc}")
        
        total_time = time.perf_counter() - start_time
        avg_time = sum(individual_times) / len(individual_times) if individual_times else 0
        
        result_data = {
            'server': self.server_name,
            'test_type': 'Paralel_Threading',
            'total_time': total_time,
            'avg_query_time': avg_time,
            'query_count': len(user_ids),
            'max_workers': max_workers,
            'individual_times': individual_times
        }
        
        self.results.append(result_data)
        print(f"Paralel test toplam suresi: {total_time:.3f}s")
        return result_data
    
    async def async_query(self, pool, user_id):
        try:
            async with pool.acquire() as conn:
                start_time = time.perf_counter()
                result = await conn.fetchrow("SELECT * FROM kullanicilar WHERE id = $1", user_id)
                end_time = time.perf_counter()
                return end_time - start_time, result
        except Exception as e:
            print(f"Async sorgu hatasi (ID: {user_id}): {e}")
            return 0, None
    
    async def parallel_asyncio_test(self, user_ids, pool_size=5):
        print(f"\n{self.server_name} - Paralel Test (Asyncio)")
        print("-" * 40)
        
        try:
            pool = await asyncpg.create_pool(
                host=self.connection_params['host'],
                database=self.connection_params['database'],
                user=self.connection_params['user'],
                password=self.connection_params['password'],
                min_size=1,
                max_size=pool_size
            )
            
            start_time = time.perf_counter()
            
            tasks = [self.async_query(pool, user_id) for user_id in user_ids]
            results = await asyncio.gather(*tasks)
            
            total_time = time.perf_counter() - start_time
            
            await pool.close()
            
            individual_times = [r[0] for r in results if r[0] > 0]
            avg_time = sum(individual_times) / len(individual_times) if individual_times else 0
            
            for i, (exec_time, _) in enumerate(results):
                print(f"Async {i+1:2d}/10: {exec_time:.3f}s (ID: {user_ids[i]})")
            
            result_data = {
                'server': self.server_name,
                'test_type': 'Paralel_Asyncio',
                'total_time': total_time,
                'avg_query_time': avg_time,
                'query_count': len(user_ids),
                'pool_size': pool_size,
                'individual_times': individual_times
            }
            
            self.results.append(result_data)
            print(f"Paralel test toplam suresi: {total_time:.3f}s")
            return result_data
            
        except Exception as e:
            print(f"Asyncio test hatasi: {e}")
    
    def run_all_tests(self, user_ids):
        print(f"\n=== {self.server_name} Paralel Programlama Testleri ===")
        print(f"Test: 10 ID'ye ait kullanicilari sorgulama")
        print(f"Test ID'leri: {user_ids}")
        
        sequential_result = self.sequential_test(user_ids)
        time.sleep(1)
        
        threading_result = self.parallel_threading_test(user_ids, max_workers=5)
        time.sleep(1)
        
        asyncio_result = asyncio.run(self.parallel_asyncio_test(user_ids, pool_size=5))
        
        print(f"\n{self.server_name} paralel testleri tamamlandi")
        
        print(f"\n{self.server_name} Test Sonuclari:")
        print("Test Turu          | Toplam Sure | Hizlanma")
        print("-" * 45)
        
        baseline_time = sequential_result['total_time']
        
        for result in self.results:
            test_type = result['test_type']
            total_time = result['total_time']
            speedup = baseline_time / total_time if total_time > 0 else 0
            
            print(f"{test_type:<17} | {total_time:>9.3f}s | {speedup:>6.2f}x")
    
    def save_results(self):
        filename = f'parallel_results_{self.server_name.lower().replace(" ", "_")}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"Paralel test sonuclari kaydedildi: {filename}")

def main():
    print("PostgreSQL Paralel Programlama Testleri")
    print("=" * 50)
    print("Test: 10 adet ID'ye ait kullanicilari tek tek sorgulama")
    print("Yontemler: Sirali, Paralel (Threading), Paralel (Asyncio)")
    print("=" * 50)
    
    test_user_ids = [100000, 200000, 300000, 400000, 500000, 
                     600000, 700000, 800000, 900000, 150000]
    
    print("\nServer B (Hatali Konfigürasyon) Paralel Testleri")
    tester_b = ParallelTester('10.0.2.15', 'Server_B')
    tester_b.run_all_tests(test_user_ids)
    tester_b.save_results()
    
    print("\n" + "="*50)
    print("Sunucular arasi gecis bekleme suresi...")
    time.sleep(5)
    
    print("\nServer A (Optimum Konfigürasyon) Paralel Testleri")
    tester_a = ParallelTester('localhost', 'Server_A')
    tester_a.run_all_tests(test_user_ids)
    tester_a.save_results()
    
    print("\nTum paralel testler tamamlandi")
    print("Olusturulan dosyalar:")
    print("- parallel_results_server_b.json")
    print("- parallel_results_server_a.json")
    
    print("\n" + "="*50)
    print("Paralel Programlama Karsilastirmasi")
    print("="*50)
    
    try:
        with open('parallel_results_server_a.json', 'r') as f:
            results_a = json.load(f)
        with open('parallel_results_server_b.json', 'r') as f:
            results_b = json.load(f)
        
        print("Test Turu          | Server A (s) | Server B (s) | A Hizlanma | B Hizlanma")
        print("-" * 75)
        
        for test_type in ['Sirali', 'Paralel_Threading', 'Paralel_Asyncio']:
            result_a = next((r for r in results_a if r['test_type'] == test_type), None)
            result_b = next((r for r in results_b if r['test_type'] == test_type), None)
            
            if result_a and result_b:
                time_a = result_a['total_time']
                time_b = result_b['total_time']
                
                baseline_a = next((r['total_time'] for r in results_a if r['test_type'] == 'Sirali'), 1)
                baseline_b = next((r['total_time'] for r in results_b if r['test_type'] == 'Sirali'), 1)
                
                speedup_a = baseline_a / time_a if time_a > 0 else 0
                speedup_b = baseline_b / time_b if time_b > 0 else 0
                
                print(f"{test_type:<17} | {time_a:>8.3f}    | {time_b:>8.3f}    | {speedup_a:>7.2f}x | {speedup_b:>7.2f}x")
        
        print("\nSonuc Analizi:")
        print("- Sirali: Baseline test (1.0x hizlanma)")
        print("- Paralel testlerde hizlanma beklenir")
        print("- Optimum konfigürasyonda daha iyi paralel performans beklenir")
        
    except Exception as e:
        print(f"Karsilastirma hatasi: {e}")

if __name__ == "__main__":
    main()
