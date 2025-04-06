#!/bin/bash
# Script to run a program for different schedules, chunk sizes and number of threads

gcc -fopenmp random_numbers.c -o random_numbers

# Size of the random number array
size=$((2 ** 30))
# Array of schedule parameters
schedules=("dynamic" "static")
# Maximum chunk size
max_chunk_size=$((2 ** 27))
# Maximum number of threads
max_threads_count=$(nproc)
# Number of repetitions per (schedule, chunk_size) combination
num_repetitions=5

# Loop over the number of threads starting from 1 and incrementing by 1 each time until it reaches max
for ((threads_count = 1; threads_count <= max_threads_count; threads_count++)); do
  export OMP_NUM_THREADS=$threads_count
  echo "Running with $threads_count threads:"

  for schedule in "${schedules[@]}"; do
    echo "Schedule: $schedule"
    printf "chunk_size,average_time\n"

    # Start from chunk size 1 and double it until it reaches max_chunk_size
    for ((chunk_size = 1; chunk_size <= max_chunk_size; chunk_size *= 2)); do
      total_time=0

      for ((rep = 1; rep <= num_repetitions; rep++)); do
        run_time=$(./random_numbers $schedule $chunk_size $size | tail -n 1)
        total_time=$(awk -v t="$total_time" -v rt="$run_time" 'BEGIN{print t+rt}')
      done

      average_time=$(awk -v tt="$total_time" -v nr="$num_repetitions" 'BEGIN{print tt/nr}')
      printf "%d,%.8f\n" "$chunk_size" "$average_time"
    done

    echo ""
  done

  echo ""
done
