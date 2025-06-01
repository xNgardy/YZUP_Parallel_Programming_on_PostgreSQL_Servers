#!/usr/bin/env python3
import json
import matplotlib.pyplot as plt
import numpy as np

def create_performance_chart():
    try:
        with open('performance_results_server_a.json', 'r') as f:
            results_a = json.load(f)
        with open('performance_results_server_b.json', 'r') as f:
            results_b = json.load(f)
        
        test_names = [r['query'][:25] + '...' for r in results_a]
        server_a_times = [r['execution_time'] for r in results_a]
        server_b_times = [r['execution_time'] for r in results_b]
        
        x = np.arange(len(test_names))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        bars1 = ax.bar(x - width/2, server_a_times, width, 
                       label='Server A (Optimum)', color='green', alpha=0.7)
        bars2 = ax.bar(x + width/2, server_b_times, width, 
                       label='Server B (Hatali)', color='red', alpha=0.7)
        
        ax.set_xlabel('Test Turleri')
        ax.set_ylabel('Calisma Suresi (saniye)')
        ax.set_title('PostgreSQL Performans Karsilastirmasi')
        ax.set_xticks(x)
        ax.set_xticklabels(test_names, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}s', ha='center', va='bottom', fontsize=8)
        
        for bar in bars2:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}s', ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        plt.savefig('performance_comparison.png', dpi=300, bbox_inches='tight')
        print("Performans grafigi olusturuldu: performance_comparison.png")
        
    except Exception as e:
        print(f"Performans grafigi hatasi: {e}")

def create_parallel_chart():
    try:
        with open('parallel_results_server_a.json', 'r') as f:
            results_a = json.load(f)
        with open('parallel_results_server_b.json', 'r') as f:
            results_b = json.load(f)
        
        test_types = ['Sirali', 'Paralel_Threading', 'Paralel_Asyncio']
        server_a_times = []
        server_b_times = []
        
        for test_type in test_types:
            a_result = next((r for r in results_a if r['test_type'] == test_type), None)
            b_result = next((r for r in results_b if r['test_type'] == test_type), None)
            
            server_a_times.append(a_result['total_time'] if a_result else 0)
            server_b_times.append(b_result['total_time'] if b_result else 0)
        
        x = np.arange(len(test_types))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars1 = ax.bar(x - width/2, server_a_times, width, 
                       label='Server A (Optimum)', color='blue', alpha=0.7)
        bars2 = ax.bar(x + width/2, server_b_times, width, 
                       label='Server B (Hatali)', color='orange', alpha=0.7)
        
        ax.set_xlabel('Test Turu')
        ax.set_ylabel('Toplam Sure (saniye)')
        ax.set_title('Paralel Programlama Karsilastirmasi')
        ax.set_xticks(x)
        ax.set_xticklabels(test_types)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        for bar in bars1:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.3f}s', ha='center', va='bottom')
        
        for bar in bars2:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.3f}s', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('parallel_comparison.png', dpi=300, bbox_inches='tight')
        print("Paralel grafigi olusturuldu: parallel_comparison.png")
        
    except Exception as e:
        print(f"Paralel grafigi hatasi: {e}")

def main():
    print("Grafikleri olusturuyor...")
    create_performance_chart()
    create_parallel_chart()
    print("Tum grafikler tamamlandi!")

if __name__ == "__main__":
    main()
