#!/usr/bin/env python3

from collections import Counter
import sys
import time

def word_count(filename):
    word_counter = Counter()
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            word_counter.update(line.strip().split())
    return word_counter

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <input-file>", file=sys.stderr)
        sys.exit(1)

    start_time = time.perf_counter()
    result = word_count(sys.argv[1])
    for word, count in result.most_common():
        print(f"{word}\t{count}")
    elapsed = time.perf_counter() - start_time

    print(f"Elapsed time: {elapsed:.6f} seconds", file=sys.stderr)
