#include <stdlib.h>
#include <stdio.h>
#include <omp.h>
#include <time.h>
#include <limits.h>
#include <string.h>

void fill_random_numbers(int *array, int n, char* schedule_param, int chunk_size) {
    unsigned int base_seed = (unsigned int)time(NULL);
    #pragma omp parallel
    {
        // Create a unique seed for each thread
        unsigned int thread_seed = base_seed + omp_get_thread_num();
        // Initialize thread-local random number generator
        struct drand48_data buffer;
        srand48_r(thread_seed, &buffer);
        if (strcmp(schedule_param, "dynamic") == 0) {
            #pragma omp for schedule(dynamic, chunk_size)
            for (int i = 0; i < n; i++) {
                double random_value;
                drand48_r(&buffer, &random_value); // Thread-safe random number generation
                array[i] = (int)(random_value * INT_MAX);
            }
        }
        if (strcmp(schedule_param, "static") == 0) {
            #pragma omp for schedule(static, chunk_size)
            for (int i = 0; i < n; i++) {
                double random_value;
                drand48_r(&buffer, &random_value); // Thread-safe random number generation
                array[i] = (int)(random_value * INT_MAX);
            }
        }
    }
}

int main(int argc, char** argv) {
    if (argc < 4) {
        fprintf(stderr, "Usage: %s <schedule_param> <chunk_size> <array_size>\n", argv[0]);
        exit(1);
    }

    char* schedule_param = argv[1];
    int chunk_size = atoi(argv[2]);
    int array_size = atoi(argv[3]);

    int *result = (int*) malloc(array_size * sizeof(int));
    double start_time, end_time;
    start_time = omp_get_wtime();

    fill_random_numbers(result, array_size, schedule_param, chunk_size);

    end_time = omp_get_wtime();
    printf("%f\n", end_time - start_time);

    free(result);
    return 0;
}
