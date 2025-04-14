#!/bin/bash -l
#SBATCH --job-name=bucket_sort
#SBATCH --nodes=1
#SBATCH --ntasks=12
#SBATCH --time=12:00:00
#SBATCH --partition=plgrid
#SBATCH --account=plgmpr25-cpu

# Helper function to print to both console and file
log() {
  echo "$1" | tee -a run.out
}

# Clean up any existing output file
rm -f run.out

# Compile the program
gcc -fopenmp bucket_sort_alg4.c -o bucket_sort_alg4

# Configuration parameters
NUM_REPETITIONS=5          # Number of times to run each test
THREAD_COUNTS=(1 2 4 8 12) # Specific thread counts to test

# Array size configuration (powers of 2)
MIN_ARRAY_EXP=10 # 2^10 = 1,024
MAX_ARRAY_EXP=26 # 2^26 = 67,108,864
ARRAY_EXP_STEP=2 # Test every 2nd power of 2

# Bucket capacity configuration (powers of 2)
MIN_BUCKET_CAPACITY_EXP=4  # 2^4 = 16
MAX_BUCKET_CAPACITY_EXP=16 # 2^16 = 65,536
BUCKET_CAPACITY_EXP_STEP=2 # Test every 2nd power of 2

# Print CSV header
log "array_size,num_threads,bucket_capacity,random_time,distribute_time,sort_time,rewrite_time,total_time"

# Main testing loop
for ((array_exp = MIN_ARRAY_EXP; array_exp <= MAX_ARRAY_EXP; array_exp += ARRAY_EXP_STEP)); do
  array_size=$((2 ** array_exp))
  for num_threads in "${THREAD_COUNTS[@]}"; do
    for ((bucket_capacity_exp = MIN_BUCKET_CAPACITY_EXP; bucket_capacity_exp <= MAX_BUCKET_CAPACITY_EXP; bucket_capacity_exp += BUCKET_CAPACITY_EXP_STEP)); do
      bucket_capacity=$((2 ** bucket_capacity_exp))
      # Run the program with the specified parameters
      output=$(./bucket_sort_alg4 $array_size $num_threads $bucket_capacity $NUM_REPETITIONS)

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
