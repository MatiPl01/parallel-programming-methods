#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <time.h>
#include <limits.h>
#include <stdbool.h>

#define MIN_VALUE 0
#define MAX_VALUE INT_MAX

typedef struct {
    int *data;
    int size;
} Bucket;

void init_bucket(Bucket *bucket) {
    bucket->data = NULL;
    bucket->size = 0;
}

int get_bucket_index(int value, int num_buckets) {
    int bucket_idx = (int)((long long)value * num_buckets / (MAX_VALUE + 1LL));
    return bucket_idx < 0 ? 0 : bucket_idx >= num_buckets ? num_buckets - 1 : bucket_idx;
}

double fill_random_numbers(int *array, int n) {
    double start_time = omp_get_wtime();
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
            array[i] = (int)(random_value * (MAX_VALUE + 1.0));
        }
    }
    return omp_get_wtime() - start_time;
}

int compare_ints(const void* a, const void* b) {
    return (*(int*)a - *(int*)b);
}

void sort_bucket(int *bucket, int bucket_size) {
    if (bucket_size > 1) {
        qsort(bucket, bucket_size, sizeof(int), compare_ints);
    }
}

bool is_sorted(int *arr, int n) {
    for (int i = 1; i < n; i++) {
        if (arr[i] < arr[i-1]) return false;
    }
    return true;
}

double distribute_to_buckets(int *arr, int array_size, Bucket *buckets, int num_buckets) {
    double start_time = omp_get_wtime();

    #pragma omp parallel for schedule(guided)
    for (int i = 0; i < array_size; i++) {
        int bucket_idx = get_bucket_index(arr[i], num_buckets);
        #pragma omp atomic
        buckets[bucket_idx].size++;
    }

    #pragma omp parallel for schedule(guided)
    for (int i = 0; i < num_buckets; i++) {
        buckets[i].data = (int*)malloc(buckets[i].size * sizeof(int));
        buckets[i].size = 0;
    }

    #pragma omp parallel for schedule(guided)
    for (int i = 0; i < array_size; i++) {
        int bucket_idx = get_bucket_index(arr[i], num_buckets);
        int pos;
        #pragma omp atomic capture
        pos = buckets[bucket_idx].size++;
        buckets[bucket_idx].data[pos] = arr[i];
    }
    return omp_get_wtime() - start_time;
}

double sort_buckets(Bucket *buckets, int num_buckets) {
    double start_time = omp_get_wtime();
    
    #pragma omp parallel
    {
        #pragma omp for schedule(guided)
        for (int i = 0; i < num_buckets; i++) {
            sort_bucket(buckets[i].data, buckets[i].size);
        }
    }
    return omp_get_wtime() - start_time;
}

double rewrite_buckets_to_array(int *arr, int array_size, Bucket *buckets, int num_buckets) {
    double start_time = omp_get_wtime();
    
    int *start_positions = (int*)malloc(num_buckets * sizeof(int));
    start_positions[0] = 0;
    for (int i = 1; i < num_buckets; i++) {
        start_positions[i] = start_positions[i-1] + buckets[i-1].size;
    }

    #pragma omp parallel
    {
        #pragma omp for schedule(guided)
        for (int i = 0; i < num_buckets; i++) {
            int start_pos = start_positions[i];
            for (int j = 0; j < buckets[i].size; j++) {
                arr[start_pos + j] = buckets[i].data[j];
            }
        }
    }
    free(start_positions);    
    return omp_get_wtime() - start_time;
}

typedef struct {
    double random_time;
    double distribute_time;
    double sort_time;
    double rewrite_time;
    double total_time;
} TimingInfo;

TimingInfo bucket_sort(int *arr, int array_size, int num_buckets) {
    TimingInfo timing = {0.0, 0.0, 0.0, 0.0, 0.0};
    double start_time = omp_get_wtime();
    
    Bucket *buckets = (Bucket*)malloc(num_buckets * sizeof(Bucket));
    for (int i = 0; i < num_buckets; i++) {
        init_bucket(&buckets[i]);
    }

    timing.distribute_time = distribute_to_buckets(arr, array_size, buckets, num_buckets);
    timing.sort_time = sort_buckets(buckets, num_buckets);
    timing.rewrite_time = rewrite_buckets_to_array(arr, array_size, buckets, num_buckets);

    for (int i = 0; i < num_buckets; i++) {
        free(buckets[i].data);
    }
    free(buckets);
    
    timing.total_time = omp_get_wtime() - start_time;
    return timing;
}

TimingInfo run_multiple_times(int array_size, int num_threads, int bucket_capacity, int num_repetitions) {
    TimingInfo avg_timing = {0.0, 0.0, 0.0, 0.0, 0.0};
    
    omp_set_num_threads(num_threads);
    int num_buckets = (array_size + bucket_capacity - 1) / bucket_capacity;
    
    int *arr = (int*)malloc(array_size * sizeof(int));
    if (!arr) {
        fprintf(stderr, "Failed to allocate memory\n");
        exit(EXIT_FAILURE);
    }
    
    for (int rep = 0; rep < num_repetitions; rep++) {
        double random_time = fill_random_numbers(arr, array_size);
        TimingInfo timing = bucket_sort(arr, array_size, num_buckets);
        bool sorted = is_sorted(arr, array_size);

        if (!sorted) {
            fprintf(stderr, "Array not sorted correctly in repetition %d\n", rep + 1);
            free(arr);
            exit(EXIT_FAILURE);
        }
        
        avg_timing.random_time += random_time;
        avg_timing.distribute_time += timing.distribute_time;
        avg_timing.sort_time += timing.sort_time;
        avg_timing.rewrite_time += timing.rewrite_time;
        avg_timing.total_time += timing.total_time;
    }

    avg_timing.random_time /= num_repetitions;
    avg_timing.distribute_time /= num_repetitions;
    avg_timing.sort_time /= num_repetitions;
    avg_timing.rewrite_time /= num_repetitions;
    avg_timing.total_time /= num_repetitions;
    free(arr);
    
    return avg_timing;
}

void print_timing_info(int array_size, int num_threads, int bucket_capacity, TimingInfo avg_timing) {
    printf("%d,%d,%d,%.10f,%.10f,%.10f,%.10f,%.10f\n", 
        array_size, 
        num_threads,
        bucket_capacity,
        avg_timing.random_time,     
        avg_timing.distribute_time, 
        avg_timing.sort_time,       
        avg_timing.rewrite_time,    
        avg_timing.total_time);
}

int main(int argc, char** argv) {
    if (argc != 5) {
        fprintf(stderr, "Usage: %s <array_size> <num_threads> <bucket_capacity> <num_repetitions>\n", argv[0]);
        return 1;
    }

    int array_size = atoi(argv[1]);
    int num_threads = atoi(argv[2]);
    int bucket_capacity = atoi(argv[3]);
    int num_repetitions = atoi(argv[4]);

    if (array_size <= 0 || num_threads <= 0 || bucket_capacity <= 0 || num_repetitions <= 0) {
        fprintf(stderr, "Error: All parameters should be positive integers\n");
        return 1;
    }

    TimingInfo avg_timing = run_multiple_times(array_size, num_threads, bucket_capacity, num_repetitions);
    print_timing_info(array_size, num_threads, bucket_capacity, avg_timing);
    return 0;
}
