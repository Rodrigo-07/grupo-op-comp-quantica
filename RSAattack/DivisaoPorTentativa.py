import math
from typing import Tuple, Dict, Any


def trial_division_basic(n: int, e: int) -> Tuple[int | None, int | None, Dict[str, Any]]:
    limit = math.isqrt(n)
    steps = 0

    if n % 2 == 0:
        return (2, n // 2, {"steps": 1})

    for d in range(3, limit + 1, 2):
        steps += 1
        if n % d == 0:
            return (d, n // d, {"steps": steps})

    return (None, None, {"steps": steps})


def trial_division_with_primes(n: int, e: int, primes: list = None) -> Tuple[int | None, int | None, Dict[str, Any]]:
    if primes is None:
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    
    steps = 0
    limit = math.isqrt(n)

    for p in primes:
        steps += 1
        if p > limit:
            break
        if n % p == 0:
            return (p, n // p, {"steps": steps, "used_prime_list": True})

    d = 101
    while d <= limit:
        steps += 1
        if n % d == 0:
            return (d, n // d, {"steps": steps, "used_prime_list": True})
        d += 2

    return (None, None, {"steps": steps, "used_prime_list": True})


def trial_division_wheel(n: int, e: int) -> Tuple[int | None, int | None, Dict[str, Any]]:
    for p in [2, 3, 5]:
        if n % p == 0:
            return (p, n // p, {"steps": 1, "wheel_optimized": True})

    increments = [4, 2, 4, 2, 4, 6, 2, 6]
    d = 7
    steps = 3
    i = 0
    limit = math.isqrt(n)

    while d <= limit:
        steps += 1
        if n % d == 0:
            return (d, n // d, {"steps": steps, "wheel_optimized": True})
        d += increments[i]
        i = (i + 1) % len(increments)

    return (None, None, {"steps": steps, "wheel_optimized": True})


def trial_division_factorization(n: int, e: int) -> Tuple[int | None, int | None, Dict[str, Any]]:
    factors = []
    original_n = n
    steps = 0

    while n % 2 == 0:
        factors.append(2)
        n //= 2
        steps += 1

    d = 3
    limit = math.isqrt(n)

    while d <= limit:
        steps += 1
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 2

    if n > 1:
        factors.append(n)

    if len(factors) >= 2:
        return (factors[0], original_n // factors[0], {"steps": steps, "all_factors": factors})
    
    return (None, None, {"steps": steps, "all_factors": factors})


def trial_division_progress(n: int, e: int, progress_interval: int = 100) -> Tuple[int | None, int | None, Dict[str, Any]]:
    limit = math.isqrt(n)
    steps = 0
    max_progress_printed = 0

    if n % 2 == 0:
        return (2, n // 2, {"steps": 1})

    for d in range(3, limit + 1, 2):
        steps += 1

        if steps % progress_interval == 0:
            percent = (d / limit) * 100
            print(f"   [Trial Division] {percent:.1f}% ({d}/{limit}) testados...")
            max_progress_printed = steps

        if n % d == 0:
            return (d, n // d, {"steps": steps, "max_progress": max_progress_printed})

    return (None, None, {"steps": steps, "max_progress": max_progress_printed})


if __name__ == "__main__":
    from BaseAttack import RSABenchmark, print_final_report

    bench = RSABenchmark(
        key_sizes_bits=(16, 20, 24, 28),
        seed=42,
    )

    print("\n========== TESTE 1: TRIAL DIVISION BÁSICO ==========")
    results_basic = bench.run(trial_division_basic)
    print_final_report(results_basic)

    bench = RSABenchmark(
        key_sizes_bits=(16, 20, 24, 28),
        seed=42,
    )

    print("\n========== TESTE 2: TRIAL DIVISION COM PRIMOS ==========")
    results_primes = bench.run(trial_division_with_primes)
    print_final_report(results_primes)

    bench = RSABenchmark(
        key_sizes_bits=(16, 20, 24, 28),
        seed=42,
    )

    print("\n========== TESTE 3: TRIAL DIVISION WHEEL ==========")
    results_wheel = bench.run(trial_division_wheel)
    print_final_report(results_wheel)

    bench = RSABenchmark(
        key_sizes_bits=(16, 20, 24, 28),
        seed=42,
    )

    print("\n========== TESTE 4: TRIAL DIVISION FATORAÇÃO COMPLETA ==========")
    results_factorization = bench.run(trial_division_factorization)
    print_final_report(results_factorization)

    bench = RSABenchmark(
        key_sizes_bits=(16, 20, 24, 28),
        seed=42,
    )

    print("\n========== TESTE 5: TRIAL DIVISION COM PROGRESSO ==========")
    results_progress = bench.run(trial_division_progress, progress_interval=50)
    print_final_report(results_progress)