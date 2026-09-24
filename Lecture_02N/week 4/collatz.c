#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <omp.h>

// Modify this with your calculated N based on your Student ID
#ifndef N_WORKLOAD
#define N_WORKLOAD 13222000ULL
#endif

#define MOD_VAL 1000000007ULL
#define MAX_THREADS 64

// Cache padding structure to eliminate false sharing
struct PaddedCounter {
    uint64_t count;
    char pad[56]; // 64 bytes total cache-line size (8 + 56 = 64)
};

// Collatz Stopping Time Kernel
static inline uint32_t collatz_steps(uint64_t n) {
    uint32_t steps = 0;
    while (n > 1) {
        if ((n & 1) == 0) n >>= 1;
        else n = 3 * n + 1;
        steps++;
    }
    return steps;
}

int main(int argc, char *argv[]) {
    uint64_t N = N_WORKLOAD;
    printf("=== OpenMP Amdahl Reality Gap Lab ===\n");
    printf("Target Workload N: %llu\n", (unsigned long long)N);
    printf("Max OpenMP Threads: %d\n\n", omp_get_max_threads());

    // -------------------------------------------------------------
    // Phase 2: Sequential Baseline
    // -------------------------------------------------------------
    printf("--- Phase 2: Sequential Baseline ---\n");
    uint32_t max_steps_seq = 0;
    uint64_t checksum_seq = 0;

    // Discard Run 1 (Cold Cache Warmup)
    for (uint64_t i = 1; i <= N; i++) {
        uint32_t st = collatz_steps(i);
        if (st > max_steps_seq) max_steps_seq = st;
        checksum_seq = (checksum_seq + st) % MOD_VAL;
    }

    // Measured Runs
    double t_seq_runs[2];
    for (int run = 0; run < 2; run++) {
        max_steps_seq = 0;
        checksum_seq = 0;
        double start = omp_get_wtime();
        for (uint64_t i = 1; i <= N; i++) {
            uint32_t st = collatz_steps(i);
            if (st > max_steps_seq) max_steps_seq = st;
            checksum_seq = (checksum_seq + st) % MOD_VAL;
        }
        t_seq_runs[run] = omp_get_wtime() - start;
    }
    double t_seq = (t_seq_runs[0] + t_seq_runs[1]) / 2.0;
    printf("Sequential Time (T_seq): %.6f s | Max Steps: %u | Checksum: %llu\n\n", 
           t_seq, max_steps_seq, (unsigned long long)checksum_seq);

    // -------------------------------------------------------------
    // Phase 3: Parallel Scaling Benchmark
    // -------------------------------------------------------------
    printf("--- Phase 3: Parallel Thread Scaling ---\n");
    int thread_counts[] = {1, 2, 4, 8, 12};
    int num_tests = sizeof(thread_counts) / sizeof(thread_counts[0]);

    for (int t = 0; t < num_tests; t++) {
        int threads = thread_counts[t];
        if (threads > omp_get_max_threads()) continue;

        double times[3];
        for (int r = 0; r < 3; r++) {
            uint32_t max_s = 0;
            double start = omp_get_wtime();
            
            #pragma omp parallel for num_threads(threads) reduction(max:max_s) schedule(static)
            for (uint64_t i = 1; i <= N; i++) {
                uint32_t st = collatz_steps(i);
                if (st > max_s) max_s = st;
            }
            times[r] = omp_get_wtime() - start;
        }
        double avg_t = (times[1] + times[2]) / 2.0; // Discard run 1 (cold)
        double speedup = t_seq / avg_t;
        printf("Threads: %2d | Run 1: %.4fs | Run 2: %.4fs | Run 3: %.4fs | Avg T_k: %.4fs | Speedup: %.2fx\n",
               threads, times[0], times[1], times[2], avg_t, speedup);
    }

    // -------------------------------------------------------------
    // Phase 4: Hardware Penalties & Micro-Architectural Experiments
    // -------------------------------------------------------------
    printf("\n--- Phase 4: Experiment A - False Sharing ---\n");
    int max_t = omp_get_max_threads();

    // Naive Implementation (Triggers False Sharing)
    int hit_count_naive[MAX_THREADS] = {0};
    double start_fs = omp_get_wtime();
    #pragma omp parallel for num_threads(max_t) schedule(static)
    for (uint64_t i = 1; i <= N; i++) {
        if (collatz_steps(i) > 100) {
            hit_count_naive[omp_get_thread_num()]++;
        }
    }
    double t_false_sharing = omp_get_wtime() - start_fs;

    // Mitigated Implementation (Reduction)
    uint64_t total_hits_reduction = 0;
    double start_red = omp_get_wtime();
    #pragma omp parallel for num_threads(max_t) reduction(+:total_hits_reduction) schedule(static)
    for (uint64_t i = 1; i <= N; i++) {
        if (collatz_steps(i) > 100) {
            total_hits_reduction++;
        }
    }
    double t_mitigated = omp_get_wtime() - start_red;

    printf("Variant 1 (Naive - False Sharing) : %.6f s\n", t_false_sharing);
    printf("Variant 2 (Reduction - Mitigated) : %.6f s\n", t_mitigated);
    printf("Penalty Ratio (Naive / Mitigated): %.2fx slowdown\n", t_false_sharing / t_mitigated);

    printf("\n--- Phase 4: Experiment B - OpenMP Loop Scheduling ---\n");
    // 1. Static Default
    double start_sch = omp_get_wtime();
    #pragma omp parallel for num_threads(max_t) schedule(static)
    for (uint64_t i = 1; i <= N; i++) { collatz_steps(i); }
    printf("schedule(static)           : %.6f s\n", omp_get_wtime() - start_sch);

    // 2. Static 1000
    start_sch = omp_get_wtime();
    #pragma omp parallel for num_threads(max_t) schedule(static, 1000)
    for (uint64_t i = 1; i <= N; i++) { collatz_steps(i); }
    printf("schedule(static, 1000)     : %.6f s\n", omp_get_wtime() - start_sch);

    // 3. Dynamic 100
    start_sch = omp_get_wtime();
    #pragma omp parallel for num_threads(max_t) schedule(dynamic, 100)
    for (uint64_t i = 1; i <= N; i++) { collatz_steps(i); }
    printf("schedule(dynamic, 100)     : %.6f s\n", omp_get_wtime() - start_sch);

    // 4. Dynamic 10000
    start_sch = omp_get_wtime();
    #pragma omp parallel for num_threads(max_t) schedule(dynamic, 10000)
    for (uint64_t i = 1; i <= N; i++) { collatz_steps(i); }
    printf("schedule(dynamic, 10000)   : %.6f s\n", omp_get_wtime() - start_sch);

    // 5. Guided
    start_sch = omp_get_wtime();
    #pragma omp parallel for num_threads(max_t) schedule(guided)
    for (uint64_t i = 1; i <= N; i++) { collatz_steps(i); }
    printf("schedule(guided)           : %.6f s\n", omp_get_wtime() - start_sch);

    return 0;
}