#!/bin/bash

# Helper function to print to both console and file
log() {
  echo "$1" | tee -a run2.out
}

# Remove existing output file if it exists
rm -f run2.out

# Compile the OpenMP program
gcc -fopenmp random_numbers.c -o random_numbers

# Array of schedule parameters
schedules=("dynamic" "static" "guided")
chunk_size=$((2 ** 6))

min_power=10 # Smallest size remains 2^10
max_power=30 # Increasing the maximum size to 2^30

max_threads_count=$(nproc)
num_repetitions=50

for schedule in "${schedules[@]}"; do
  log "Schedule: $schedule"

  for ((threads_count = 1; threads_count <= max_threads_count; threads_count++)); do
    export OMP_NUM_THREADS=$threads_count
    log "Number of threads: $threads_count"
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
  done
  log ""
done
