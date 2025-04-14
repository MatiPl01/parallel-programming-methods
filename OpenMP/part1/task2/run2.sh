#!/bin/bash

# Helper function to print to both console and file
log() {
  echo "$1" | tee -a run2.out
}

# Helper function to run measurements for a given configuration
run_measurements() {
  local schedule=$1
  local threads=$2
  local label=$3

  export OMP_NUM_THREADS=$threads
  log "$label (threads: $threads)"
  log "array_size,average_time"

  # Vary the array size
  for ((power = min_power; power <= max_power; power++)); do
    size=$((2 ** power))
    total_time=0

    # Compute the total_time as the sum of several runs
    for ((rep = 1; rep <= num_repetitions; rep++)); do
      run_time=$(./random_numbers $schedule $chunk_size $size | tail -n 1)
      total_time=$(awk -v t="$total_time" -v rt="$run_time" 'BEGIN{printf "%.10f", t+rt}')
    done

    # Calculate average time from the total time
    average_time=$(awk -v tt="$total_time" -v nr="$num_repetitions" 'BEGIN{printf "%.10f", tt/nr}')
    log "$size,$average_time"
  done
  log ""
}

# Remove existing output file if it exists
rm -f run2.out

# Compile the OpenMP program
gcc -fopenmp random_numbers.c -o random_numbers

# Configuration parameters
schedules=("dynamic" "static" "guided")
chunk_size=$((2 ** 6))
min_power=10
max_power=30
max_threads_count=$(nproc)
num_repetitions=50

# Run synchronous (single-threaded) case without OpenMP usage
run_measurements "static" 1 "synchronous"

for ((threads = 2; threads <= max_threads_count; threads++)); do
  for schedule in "${schedules[@]}"; do
    # Run parallel cases with different schedules and thread counts
    run_measurements "$schedule" $threads "Schedule: $schedule"
  done
done
