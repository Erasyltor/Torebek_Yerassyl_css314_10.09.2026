from concurrent.futures import ThreadPoolExecutor
import threading
import time
import math


def worker_task(thread_id, team_size):
    native_tid = threading.get_native_id()
    role = "Master" if thread_id == 0 else "Worker"


    time.sleep(0.001 * (thread_id % 3))
    result = 0.0
    for i in range(10_000_000):
        result += math.sqrt(i)
    print(
        f"[{role}] Logical Rank: {thread_id} of {team_size} "
        f"| Native OS TID: {native_tid}"
    )


def run_team(num_threads):
    print(f"--- Forking a team of {num_threads} threads ---")

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(worker_task, tid, num_threads)
            for tid in range(num_threads)
        ]
        for future in futures:
            future.result()

    print("--- Joined thread team. Execution returned to serial master ---\n")


if __name__ == "__main__":
    for p in [1, 2, 4, 8, 16, 32, 64]:
        start = time.perf_counter()
        run_team(p)
        elapsed = time.perf_counter() - start
        print(f"{p} threads: {elapsed:.6f} seconds")