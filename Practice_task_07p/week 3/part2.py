import random
import threading
import time

totalHits = 0
lock = threading.Lock()


def SyncMonteCarloTask(points_per_thread):
  global totalHits
  for _ in range(points_per_thread):
    x = random.random()
    y = random.random()
    if x * x + y * y <= 1.0:
      with lock:  # Synchronization lock
        totalHits += 1


def SingleThreadTask(total_points):
  hits = 0
  for _ in range(total_points):
    x = random.random()
    y = random.random()
    if x * x + y * y <= 1.0:
      hits += 1
  return hits


def main():
  total_points = 50_000_000

  # Single-threaded baseline
  start_single = time.time()
  single_hits = SingleThreadTask(total_points)
  time_single = (time.time() - start_single) * 1000
  pi_single = 4.0 * single_hits / total_points

  # Multi-threaded with Lock
  num_threads = 4
  points_per_thread = total_points // num_threads
  threads = []

  start_multi = time.time()
  for _ in range(num_threads):
    t = threading.Thread(
        target=SyncMonteCarloTask, args=(points_per_thread,)
    )
    threads.append(t)
    t.start()

  for t in threads:
    t.join()

  time_multi = (time.time() - start_multi) * 1000
  pi_multi = 4.0 * totalHits / total_points

  print(
      f'Single-threaded: Time = {time_single:.2f} ms, Pi ='
      f' {pi_single:.5f}'
  )
  print(
      f'Multi-threaded (Locked): Time = {time_multi:.2f} ms, Pi ='
      f' {pi_multi:.5f}'
  )


if __name__ == '__main__':
  main()