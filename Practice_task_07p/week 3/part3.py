import multiprocessing
import random
import time


def WorkerReduction(points):
    hits = 0

    for _ in range(points):
        x = random.random()
        y = random.random()

        if x * x + y * y <= 1.0:
            hits += 1

    return hits


def Benchmark(total_points, T):
    points_per_process = total_points // T

    start = time.time()

    with multiprocessing.Pool(processes=T) as pool:
        results = pool.map(
            WorkerReduction,
            [points_per_process] * T
        )

    duration_ms = (time.time() - start) * 1000

    return duration_ms


def main():
    total_points = 100_000_000
    thread_counts = [1, 2, 4, 8, 16, 32]

    print(f'{"Processes (T)":<15} | {"Runtime (ms)":<14} | {"Speedup":<12} | {"Efficiency":<12}')
    print('-' * 65)

    baseline_time = 0.0

    for T in thread_counts:

        duration = Benchmark(total_points, T)

        if T == 1:
            baseline_time = duration

        speedup = baseline_time / duration
        efficiency = (speedup / T) * 100.0

        print(
            f'{T:<15} | '
            f'{duration:<14.2f} | '
            f'{speedup:<12.2f}x | '
            f'{efficiency:.1f}%'
        )


if __name__ == '__main__':
    main()