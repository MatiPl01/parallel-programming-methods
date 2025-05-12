#!/usr/bin/env python
from collections import Counter

def word_count(filename):
    word_counter = Counter()
    with open(filename, 'r', encoding='latin-1') as f:
        for line in f:
            words = line.strip().split()
            word_counter.update(words)
    return word_counter

if __name__ == '__main__':
    from sys import argv
    import time
    start_time = time.perf_counter()
    result = word_count(argv[1])
    elapsed = time.perf_counter() - start_time
    for word, count in result.most_common(10):
        print(word, count)
    print(f"Elapsed time: {elapsed:.6f} seconds")
