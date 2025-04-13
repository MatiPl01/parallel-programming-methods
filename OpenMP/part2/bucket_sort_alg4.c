#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <string.h>
#include <time.h>
#include <limits.h>
#include <stdbool.h>
#include <stdlib.h>

#define MIN_VALUE 0  // Minimum value in the array
#define MAX_VALUE INT_MAX  // Maximum value in the array

// Structure to represent a dynamic bucket
typedef struct {
    int *data;
    int size;
    int capacity;
} Bucket;

// Function to initialize a bucket
void init_bucket(Bucket *bucket, int initial_capacity) {
    bucket->data = (int*)malloc(initial_capacity * sizeof(int));
    bucket->size = 0;
    bucket->capacity = initial_capacity;
}

// Function to add an element to a bucket
void add_to_bucket(Bucket *bucket, int value) {
    if (bucket->size >= bucket->capacity) {
        // Double the capacity
        bucket->capacity *= 2;
        bucket->data = (int*)realloc(bucket->data, bucket->capacity * sizeof(int));
    }
    bucket->data[bucket->size++] = value;
}

// Helper function to calculate bucket index
int get_bucket_index(int value, int num_buckets) {
    int bucket_idx = (int)((long long)(value - MIN_VALUE) * num_buckets / (MAX_VALUE - MIN_VALUE));
    if (bucket_idx >= num_buckets) bucket_idx = num_buckets - 1;
    if (bucket_idx < 0) bucket_idx = 0;
    return bucket_idx;
}

// Function to fill the array with random numbers using guided scheduling
double fill_random_numbers(int *array, int n) {
    double start_time = omp_get_wtime();
    unsigned int base_seed = (unsigned int)time(NULL);
    
    #pragma omp parallel
    {
        // Create a unique seed for each thread
        unsigned int thread_seed = base_seed + omp_get_thread_num();
        // Initialize thread-local random number generator
        // Note: Ignoring linter error for struct drand48_data as this implementation is correct
        struct drand48_data buffer;
        srand48_r(thread_seed, &buffer);
        
        #pragma omp for schedule(guided)
        for (int i = 0; i < n; i++) {
            double random_value;
            drand48_r(&buffer, &random_value);
            array[i] = (int)(random_value * MAX_VALUE);
        }
    }
    return omp_get_wtime() - start_time;
}

// Insertion sort algorithm for sorting individual buckets
void insertion_sort(int *bucket, int bucket_size) {
    for (int i = 1; i < bucket_size; i++) {
        int value = bucket[i];
        int j = i - 1;
        while (j >= 0 && bucket[j] > value) {
            bucket[j + 1] = bucket[j];
            j--;
        }
        bucket[j + 1] = value;
    }
}

// Function to verify if array is sorted
bool is_sorted(int *arr, int n) {
    for (int i = 1; i < n; i++) {
        if (arr[i] < arr[i-1]) return false;
    }
    return true;
}

// Function to distribute elements to buckets
double distribute_to_buckets(int *arr, int array_size, Bucket *buckets, int num_buckets) {
    double start_time = omp_get_wtime();
    
    #pragma omp parallel
    {
        // Each thread reads its own portion of the array
        #pragma omp for schedule(guided)
        for (int i = 0; i < array_size; i++) {
            // Calculate bucket index
            int bucket_idx = get_bucket_index(arr[i], num_buckets);
            
            int position;
            // Atomically get the position and increment the size
            #pragma omp atomic capture
            {
                position = buckets[bucket_idx].size;
                buckets[bucket_idx].size++;
            }
            
            // Check if we need to resize the bucket
            if (position >= buckets[bucket_idx].capacity) {
                // Use a critical section for resizing to avoid race conditions
                #pragma omp critical
                {
                    // Double check if we still need to resize (another thread might have already done it)
                    if (position >= buckets[bucket_idx].capacity) {
                        // Double the capacity
                        int new_capacity = buckets[bucket_idx].capacity * 2;
                        int *new_data = (int*)realloc(buckets[bucket_idx].data, new_capacity * sizeof(int));
                        
                        // Update the bucket with new data and capacity
                        buckets[bucket_idx].data = new_data;
                        buckets[bucket_idx].capacity = new_capacity;
                    }
                }
            }
            
            // Add the element to the bucket
            buckets[bucket_idx].data[position] = arr[i];
        }
    }
    
    return omp_get_wtime() - start_time;
}

// Function to sort buckets
double sort_buckets(Bucket *buckets, int num_buckets) {
    double start_time = omp_get_wtime();
    
    #pragma omp parallel
    {
        // Each thread processes a subset of buckets
        #pragma omp for schedule(dynamic, 1)
        for (int i = 0; i < num_buckets; i++) {
            // Sort the bucket
            insertion_sort(buckets[i].data, buckets[i].size);
        }
    }
    
    return omp_get_wtime() - start_time;
}

// Function to rewrite sorted buckets back to the original array
double rewrite_buckets_to_array(int *arr, int array_size, Bucket *buckets, int num_buckets) {
    double start_time = omp_get_wtime();
    
    // Calculate starting positions for each bucket
    int *start_positions = (int*)malloc(num_buckets * sizeof(int));
    start_positions[0] = 0;
    for (int i = 1; i < num_buckets; i++) {
        start_positions[i] = start_positions[i-1] + buckets[i-1].size;
    }
    
    // Rewrite sorted buckets back to the original array
    #pragma omp parallel
    {
        // Each thread processes a subset of buckets
        #pragma omp for schedule(dynamic, 1)
        for (int i = 0; i < num_buckets; i++) {
            // Get the starting position for this bucket
            int start_pos = start_positions[i];
            
            // Write the sorted bucket data to the original array
            for (int j = 0; j < buckets[i].size; j++) {
                arr[start_pos + j] = buckets[i].data[j];
            }
        }
    }
    
    free(start_positions);
    return omp_get_wtime() - start_time;
}

// Structure to hold timing information
typedef struct {
    double random_time;
    double distribute_time;
    double sort_time;
    double rewrite_time;
    double total_time;
} TimingInfo;

// Bucket sort algorithm that takes an input array and sorts it in-place
TimingInfo bucket_sort(int *arr, int array_size, int num_buckets, int initial_bucket_capacity) {
    TimingInfo timing = {0.0, 0.0, 0.0, 0.0, 0.0};
    double start_time = omp_get_wtime();
    
    // Allocate memory for buckets
    Bucket *buckets = (Bucket*)malloc(num_buckets * sizeof(Bucket));
    for (int i = 0; i < num_buckets; i++) {
        init_bucket(&buckets[i], initial_bucket_capacity);
    }

    // Step 1: Distribute numbers to buckets
    timing.distribute_time = distribute_to_buckets(arr, array_size, buckets, num_buckets);

    // Step 2: Sort buckets
    timing.sort_time = sort_buckets(buckets, num_buckets);
    
    // Step 3: Rewrite sorted buckets back to the original array
    timing.rewrite_time = rewrite_buckets_to_array(arr, array_size, buckets, num_buckets);

    // Free allocated memory
    for (int i = 0; i < num_buckets; i++) {
        free(buckets[i].data);
    }
    free(buckets);
    
    timing.total_time = omp_get_wtime() - start_time;
    
    return timing;
}

// Function to run multiple repetitions and calculate averages
TimingInfo run_multiple_times(int array_size, int num_threads, int num_buckets, int initial_bucket_capacity, int num_repetitions) {
    TimingInfo avg_timing = {0.0, 0.0, 0.0, 0.0, 0.0};
    
    // Set number of threads
    omp_set_num_threads(num_threads);
    
    // Allocate memory for the array
    int *arr = (int*)malloc(array_size * sizeof(int));
    if (!arr) {
        fprintf(stderr, "Failed to allocate memory\n");
        exit(1);
    }
    
    // Run the test multiple times
    for (int rep = 0; rep < num_repetitions; rep++) {
        // Fill the array with random numbers
        double random_time = fill_random_numbers(arr, array_size);
        
        // Sort the array using bucket sort
        TimingInfo timing = bucket_sort(arr, array_size, num_buckets, initial_bucket_capacity);
        
        // Verify sorting
        bool sorted = is_sorted(arr, array_size);
        
        // If not sorted, log error and exit
        if (!sorted) {
            fprintf(stderr, "Error: Array was not sorted correctly in repetition %d\n", rep + 1);
            free(arr);
            exit(1);
        }
        
        // Accumulate timing information
        avg_timing.random_time += random_time;
        avg_timing.distribute_time += timing.distribute_time;
        avg_timing.sort_time += timing.sort_time;
        avg_timing.rewrite_time += timing.rewrite_time;
        avg_timing.total_time += timing.total_time;
    }
    
    // Calculate averages
    avg_timing.random_time /= num_repetitions;
    avg_timing.distribute_time /= num_repetitions;
    avg_timing.sort_time /= num_repetitions;
    avg_timing.rewrite_time /= num_repetitions;
    avg_timing.total_time /= num_repetitions;
    
    // Free allocated memory
    free(arr);
    
    return avg_timing;
}

void print_usage(const char *program_name) {
    printf("Usage: %s <array_size> <num_threads> <num_buckets> <initial_bucket_capacity> <num_repetitions>\n", program_name);
    printf("Parameters:\n");
    printf("  array_size              Size of the array to sort\n");
    printf("  num_threads             Number of OpenMP threads to use\n");
    printf("  num_buckets             Number of buckets for bucket sort\n");
    printf("  initial_bucket_capacity Initial capacity for each bucket\n");
    printf("  num_repetitions         Number of times to run the test\n");
    printf("\nExample: %s 1000000 4 100 1024 5\n", program_name);
}

int main(int argc, char** argv) {
    // Check if all required parameters are provided
    if (argc != 6) {
        print_usage(argv[0]);
        return 1;
    }
    
    // Parse command line arguments
    int array_size = atoi(argv[1]);
    int num_threads = atoi(argv[2]);
    int num_buckets = atoi(argv[3]);
    int initial_bucket_capacity = atoi(argv[4]);
    int num_repetitions = atoi(argv[5]);
    
    // Validate parameters
    if (array_size <= 0) {
        fprintf(stderr, "Error: Array size must be positive\n");
        return 1;
    }
    if (num_threads <= 0) {
        fprintf(stderr, "Error: Number of threads must be positive\n");
        return 1;
    }
    if (num_buckets <= 0) {
        fprintf(stderr, "Error: Number of buckets must be positive\n");
        return 1;
    }
    if (initial_bucket_capacity <= 0) {
        fprintf(stderr, "Error: Initial bucket capacity must be positive\n");
        return 1;
    }
    if (num_repetitions <= 0) {
        fprintf(stderr, "Error: Number of repetitions must be positive\n");
        return 1;
    }

    // Run multiple times and calculate averages
    TimingInfo avg_timing = run_multiple_times(array_size, num_threads, num_buckets, initial_bucket_capacity, num_repetitions);
    
    // Print results in CSV format with reordered columns and higher precision
    printf("%d,%d,%d,%d,%.9f,%.9f,%.9f,%.9f,%.9f\n", 
            array_size, 
            num_threads,
            num_buckets,
            initial_bucket_capacity,
            avg_timing.random_time,      // (a) Random number generation time
            avg_timing.distribute_time,  // (b) Distribution to buckets time
            avg_timing.sort_time,        // (c) Bucket sorting time
            avg_timing.rewrite_time,     // (d) Rewriting buckets to array time
            avg_timing.total_time);      // (e) Total execution time

    return 0;
}
