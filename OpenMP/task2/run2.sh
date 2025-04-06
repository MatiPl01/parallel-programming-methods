#!/bin/bash

# Compile the OpenMP program
gcc -fopenmp random_numbers.c -o random_numbers

schedule="static"
chunk_size=$((2 ** 6))

min_power=10 # Smallest size remains 2^10
max_power=30 # Increasing the maximum size to 2^30

max_threads_count=$(nproc)
num_repetitions=20

for ((threads_count = 1; threads_count <= max_threads_count; threads_count++)); do
  export OMP_NUM_THREADS=$threads_count
  echo "Number of threads: $threads_count"
  printf "array_size,average_time\n"

  # Vary the array size
  for ((power = min_power; power <= max_power; power++)); do
    size=$((2 ** power))
    total_time=0

    # Compute the total_time as the sum of several runs
    for ((rep = 1; rep <= num_repetitions; rep++)); do
      run_time=$(./random_numbers $schedule $chunk_size $size | tail -n 1)
      total_time=$(awk -v t="$total_time" -v rt="$run_time" 'BEGIN{print t + rt}')
    done

    # Calculate average time from the total time
    average_time=$(awk -v tt="$total_time" -v nr="$num_repetitions" 'BEGIN{print tt / nr}')
    printf "%d,%.8f\n" "$size" "$average_time"
  done
  echo ""
done
