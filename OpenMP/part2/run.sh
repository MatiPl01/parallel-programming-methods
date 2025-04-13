#!/bin/bash
# Script to run bucket sort algorithm with different parameters

# Helper function to print to both console and file
log() {
  echo "$1" | tee -a run.out
}

# Clean up any existing output file
rm -f run.out

# Compile the program
gcc -fopenmp bucket_sort_alg4.c -o bucket_sort_alg4

# Configuration parameters
INITIAL_BUCKET_CAPACITY=1024 # Initial capacity for each bucket
NUM_REPETITIONS=5            # Number of times to run each test
MAX_THREADS=$(nproc)         # Maximum number of threads (number of processors)

# Array size configuration (powers of 2)
MIN_ARRAY_EXP=10 # 2^10 = 1,024
MAX_ARRAY_EXP=30 # 2^30 = 1,073,741,824
ARRAY_EXP_STEP=2 # Test every 2nd power of 2

# Bucket count configuration (powers of 2)
MIN_BUCKET_EXP=4  # 2^4 = 16
MAX_BUCKET_EXP=16 # 2^16 = 65,536
BUCKET_EXP_STEP=2 # Test every 2nd power of 2

# Print CSV header
log "array_size,num_threads,num_buckets,initial_bucket_capacity,random_time,distribute_time,sort_time,rewrite_time,total_time"

# Main testing loop
for ((array_exp = MIN_ARRAY_EXP; array_exp <= MAX_ARRAY_EXP; array_exp += ARRAY_EXP_STEP)); do
  array_size=$((2 ** array_exp))
  for ((num_threads = 1; num_threads <= MAX_THREADS; num_threads++)); do
    for ((bucket_exp = MIN_BUCKET_EXP; bucket_exp <= MAX_BUCKET_EXP; bucket_exp += BUCKET_EXP_STEP)); do
      num_buckets=$((2 ** bucket_exp))
      # Run the program with the specified parameters
      output=$(./bucket_sort_alg4 $array_size $num_threads $num_buckets $INITIAL_BUCKET_CAPACITY $NUM_REPETITIONS)

      # Check if the program exited with an error
      if [ $? -ne 0 ]; then
        log "Error: Program exited with error code. Stopping execution."
        exit 1
      fi

      # Log the results
      log "$output"
    done
  done
done
