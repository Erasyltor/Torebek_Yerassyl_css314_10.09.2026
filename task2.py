import time 
import math 
from concurrent.futures import ProcessPoolExecutor 
 
# Алгоритм: поиск простых чисел в интервале до 5,000,000 
def is_prime(n): 
    if n < 2: 
        return False 
    if n in (2, 3): 
        return True 
    if n % 2 == 0 or n % 3 == 0: 
        return False 
    for i in range(5, int(math.isqrt(n)) + 1, 6): 
        if n % i == 0 or n % (i + 5) == 0: 
            return False 
    return True 
 
def prime_range_task(start, end): 
    count = 0 
    for i in range(start, end): 
        if is_prime(i): 
            count += 1 
    return count 
 
def run_benchmark_for_threads(num_workers, max_num=5000000): 
    chunk_size = max_num // num_workers 
    ranges = [] 
    for i in range(num_workers): 
        start = i * chunk_size + 1 
        end = max_num + 1 if i == num_workers - 1 else (i + 1) * chunk_size + 1 
        ranges.append((start, end)) 
 
    start_time = time.perf_counter() 
    with ProcessPoolExecutor(max_workers=num_workers) as executor: 
        futures = [executor.submit(prime_range_task, r[0], r[1]) for r in ranges] 
        results = [f.result() for f in futures] 
    end_time = time.perf_counter() 
    return end_time - start_time 
 
def main(): 
    threads_list = [1, 2, 4, 8, 16, 32] 
    runs = 3 
    results_data = {} 
 
    print("Language & Runtime: Python (multiprocessing / ProcessPoolExecutor)\n") 
    print("Workload Algorithm: Prime Sieve / Prime Check to 5,000,000\n") 
    print("Running benchmark...") 
 
    t1_avg = None 
 
    for N in threads_list: 
        run_times = [] 
        for r in range(runs): 
            t = run_benchmark_for_threads(N) 
            run_times.append(t) 
            print(f"N={N}, Run {r+1}: {t:.4f} s") 
 
        avg_time = sum(run_times) / runs 
        if N == 1: 
            t1_avg = avg_time 
 
        speedup = t1_avg / avg_time 
        efficiency = (speedup / N) * 100 
 
        results_data[N] = { 
            'runs': run_times, 
            'avg': avg_time, 
            'speedup': speedup, 
            'efficiency': efficiency 
        } 
 
    print("\n" + "="*80) 
    print(f"{'Threads (N)':<12} | {'Run 1 (s)':<10} | {'Run 2 (s)':<10} | {'Run 3 (s)':<10} | {'Avg Time TN (s)':<15} | {'Speedup SN':<12} | {'Efficiency EN':<12}") 
    print("="*80) 
 
    for N in threads_list: 
        d = results_data[N] 
        r1, r2, r3 = d['runs'] 
        print(f"{N:<12} | {r1:<10.3f} | {r2:<10.3f} | {r3:<10.3f} | {d['avg']:<15.3f} | {d['speedup']:<12.2f}x | {d['efficiency']:<11.1f}%") 
 
if __name__ == "__main__":
    main()