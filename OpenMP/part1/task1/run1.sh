#!/bin/bash
# Script to run a program for different schedules, chunk sizes and number of threads

# Helper function to print to both console and file
log() {
  echo "$1" | tee -a run1.out
}

# Helper function to run measurements for a given configuration
run_measurements() {
  local schedule=$1
  local threads=$2
  local label=$3

  export OMP_NUM_THREADS=$threads
  log "$label (threads: $threads)"
  log "chunk_size,average_time"

  # Start from chunk size 1 and double it until it reaches max_chunk_size
  for ((chunk_size = 1; chunk_size <= max_chunk_size; chunk_size *= 2)); do
    total_time=0

    for ((rep = 1; rep <= num_repetitions; rep++)); do
      run_time=$(./random_numbers $schedule $chunk_size $size | tail -n 1)
      total_time=$(awk -v t="$total_time" -v rt="$run_time" 'BEGIN{printf "%.10f", t+rt}')
    done

    average_time=$(awk -v tt="$total_time" -v nr="$num_repetitions" 'BEGIN{printf "%.10f", tt/nr}')
    log "$chunk_size,$average_time"
  done
  log ""
}

# Remove existing output file if it exists
rm -f run1.out

gcc -fopenmp random_numbers.c -o random_numbers

# Size of the random number array
size=$((2 ** 30))
# Array of schedule parameters
schedules=("dynamic" "static" "guided")
# Maximum chunk size
max_chunk_size=$((2 ** 27))
# Maximum number of threads
max_threads_count=$(nproc)
# Number of repetitions per (schedule, chunk_size) combination
num_repetitions=5

# Run synchronous (single-threaded) case without OpenMP usage
run_measurements "static" 1 "synchronous"

for ((threads = 1; threads <= max_threads_count; threads++)); do
  for schedule in "${schedules[@]}"; do
    # Run parallel cases with different schedules and thread counts
    run_measurements "$schedule" $threads "Schedule: $schedule"
  done
done
