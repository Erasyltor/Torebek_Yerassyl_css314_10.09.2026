import random
import threading

totalHits = 0  # Shared variable causing data race


def MonteCarloTask(points_per_thread):
  global totalHits
  for _ in range(points_per_thread):
    x = random.random()
    y = random.random()
    if x * x + y * y <= 1.0:
      totalHits += 1  # Unsynchronized race condition


def main():
  total_points = 50_000_000
  num_threads = 4
  points_per_thread = total_points // num_threads

  for run in range(1, 6):
    global totalHits
    totalHits = 0

    threads = []
    for _ in range(num_threads):
      t = threading.Thread(
          target=MonteCarloTask, args=(points_per_thread,)
      )
      threads.append(t)
      t.start()

    for t in threads:
      t.join()

    pi_approx = 4.0 * totalHits / total_points
    print(f'Run {run}: Pi = {pi_approx:.5f} (Total Hits: {totalHits})')


if __name__ == '__main__':
  main()