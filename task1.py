import multiprocessing as mp
import time

PROCESSES = 10
INCREMENTS = 1_000_000
EXPECTED = PROCESSES * INCREMENTS


def unlocked_worker(counter):
    for _ in range(INCREMENTS):
        counter.value += 1


def locked_worker(counter, lock):
    for _ in range(INCREMENTS):
        with lock:
            counter.value += 1


def run_unlocked():
    counter = mp.Value("i", 0, lock=False)

    processes = []

    start = time.perf_counter()

    for _ in range(PROCESSES):
        p = mp.Process(
            target=unlocked_worker,
            args=(counter,)
        )
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    end = time.perf_counter()

    return counter.value, (end - start) * 1000


def run_locked():
    counter = mp.Value("i", 0, lock=False)
    lock = mp.Lock()

    processes = []

    start = time.perf_counter()

    for _ in range(PROCESSES):
        p = mp.Process(
            target=locked_worker,
            args=(counter, lock)
        )
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    end = time.perf_counter()

    return counter.value, (end - start) * 1000


def main():
    print("=" * 60)
    print("TASK 3 - UNSYNCHRONIZED SHARED COUNTER")
    print("=" * 60)
    print(f"Expected value: {EXPECTED:,}")
    print()

    unlocked_times = []

    print("UNLOCKED - 10 RUNS")

    for run in range(1, 11):
        value, elapsed = run_unlocked()
        error = EXPECTED - value

        unlocked_times.append(elapsed)

        print(
            f"Run #{run}: "
            f"Output = {value:,} | "
            f"Error = {error:,} | "
            f"Time = {elapsed:.2f} ms"
        )

    print()
    print("=" * 60)
    print("LOCKED VERSION")
    print("=" * 60)

    value, locked_time = run_locked()

    average_unlocked = sum(unlocked_times) / len(unlocked_times)

    print(f"Locked Output: {value:,}")
    print(f"Average Unlocked Time: {average_unlocked:.2f} ms")
    print(f"Locked Time: {locked_time:.2f} ms")


if __name__ == "__main__":
    mp.freeze_support()
    main()