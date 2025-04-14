#include <stdlib.h>
#include <stdio.h>
#include <omp.h>
#include <time.h>
#include <limits.h>
#include <string.h>

void generate_random_numbers(int *array, int n) {
    unsigned int base_seed = (unsigned int)time(NULL);
    
    #pragma omp parallel
    {
        unsigned int thread_seed = base_seed + omp_get_thread_num();
        struct drand48_data buffer;
        srand48_r(thread_seed, &buffer);
        
        #pragma omp for schedule(guided)
        for (int i = 0; i < n; i++) {
            double random_value;
            drand48_r(&buffer, &random_value);
            array[i] = (int)(random_value * INT_MAX);
        }
    }
}

int main(int argc, char** argv) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <array_size>\n", argv[0]);
        exit(1);
    }

    int array_size = atoi(argv[1]);
    int *result = (int*) malloc(array_size * sizeof(int));
    
    generate_random_numbers(result, array_size);
    
    // Print the numbers comma-separated
    for (int i = 0; i < array_size; i++) {
        printf("%d%s", result[i], (i < array_size - 1) ? "," : "\n");
    }
    
    free(result);
    return 0;
}
