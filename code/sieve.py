#!/usr/bin/python

def sieve(n=2):
    yield n
    for next in sieve(n+1):
        if next % n > 0:
            yield next

for _, prime in zip(range(100), sieve()):
    print prime,
print
