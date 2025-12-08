#!/usr/bin/env python3
"""
Quadratic Sieve (didatic but improved) - Python puro (corrigido)
- Tonelli-Shanks for sqrt mod p
- factor base selection
- log-sieve over interval [-M..M]
- trial division for candidates
- bitpacked Gaussian elimination tracking row combinations to get dependencies
- attempt factor extraction via gcd

Improvements:
- Better heuristics for B and M (suitable for ~64-bit integers)
- collect_stats option to return internal statistics for benchmarking
- wrapper quadratic_sieve_attack compatible with RSABenchmark.run(n, e, ...)
Limitations: pure Python; no large-prime variants; suitable for moderate sizes.
"""

import math
from math import isqrt, log, exp
from collections import defaultdict
import random
import time
import sys
from BaseAttack import RSABenchmark
# ---------------- Utilities ----------------

def gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a)

def is_square(n):
    s = isqrt(n)
    return s*s == n

# ---------------- Tonelli-Shanks ----------------

def tonelli_shanks(n, p):
    """Solve x^2 ≡ n (mod p). Return a root r (0 <= r < p) or None if no root.
       p must be an odd prime."""
    n %= p
    if n == 0:
        return 0
    if p == 2:
        return n
    # check residue
    if pow(n, (p - 1) // 2, p) != 1:
        return None
    # simple case
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    # factor p-1 = q * 2^s
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1
    # find z quadratic non-residue
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m = s
    c = pow(z, q, p)
    t = pow(n, q, p)
    r = pow(n, (q + 1) // 2, p)
    while True:
        if t == 0:
            return 0
        if t == 1:
            return r
        # find least i such that t^(2^i) == 1
        i = 1
        t2i = (t * t) % p
        while i < m:
            if t2i == 1:
                break
            t2i = (t2i * t2i) % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p

# ---------------- Primes ----------------

def primes_up_to(n):
    if n < 2:
        return []
    sieve = bytearray(b'\x01') * (n+1)
    sieve[0:2] = b'\x00\x00'
    for p in range(2, int(n**0.5) + 1):
        if sieve[p]:
            step = p
            start = p*p
            sieve[start:n+1:step] = b'\x00' * (((n - start)//step) + 1)
    return [i for i, isprime in enumerate(sieve) if isprime]

# ---------------- Factor base ----------------

def build_factor_base(n, B):
    primes = primes_up_to(B)
    fb = []
    for p in primes:
        if p == 2:
            fb.append(2)
        else:
            # Legendre symbol: pow(n, (p-1)//2, p) == 1 => quadratic residue
            if pow(n % p, (p-1)//2, p) == 1:
                fb.append(p)
    return fb

# ---------------- Sieving ----------------

def sieve_block(n, fb, M, a0, log_threshold=1.8):
    """
    Sieve in interval a = a0-M .. a0+M (a0 typically floor(sqrt(n))).
    Returns list of candidate tuples (a, Q = a^2 - n, factors_dict)
    where Q is B-smooth (factored over fb).
    """
    size = 2*M + 1
    start_a = a0 - M
    logs = [0.0] * size
    Qvals = [0] * size

    # compute initial logs
    for i in range(size):
        a = start_a + i
        Q = a*a - n
        Qvals[i] = Q
        if Q == 0:
            logs[i] = 0.0
        else:
            logs[i] = math.log(abs(Q))

    # precompute roots for each prime
    roots = {}
    for p in fb:
        if p == 2:
            roots[p] = [n % 2]
            continue
        r = tonelli_shanks(n % p, p)
        if r is None:
            roots[p] = []
        else:
            r2 = p - r
            if r == r2:
                roots[p] = [r]
            else:
                roots[p] = [r, r2]

    # subtract contributions log(p) where p divides Q(a)
    for p in fb:
        rlist = roots.get(p, [])
        if not rlist:
            continue
        logp = math.log(p)
        for r in rlist:
            # indices i with a ≡ r (mod p) and a = start_a + i
            i0 = (r - start_a) % p
            for i in range(i0, size, p):
                logs[i] -= logp

    candidates = []
    # choose threshold
    for i in range(size):
        a = start_a + i
        Q = Qvals[i]
        if Q == 0:
            continue
        # candidate if remaining log small enough (heuristic)
        if logs[i] <= log_threshold:
            sign = 1
            rem = Q
            if rem < 0:
                sign = -1
                rem = -rem
            exps = {}
            # trial division
            for p in fb:
                if rem % p == 0:
                    e = 0
                    while rem % p == 0:
                        rem //= p
                        e += 1
                    exps[p] = e
                if rem == 1:
                    break
                if p * p > rem:
                    # rem might be prime > B -> not smooth
                    pass
            if rem == 1:
                if sign == -1:
                    exps[-1] = 1
                candidates.append((a, Q, exps))
    return candidates

# ---------------- Matrix building & elimination ----------------

def build_matrix(relations, fb):
    """
    relations: list of (a, Q, exps_dict)
    Returns rows_bits (list of int bitmasks) and col_list
    """
    have_minus1 = any((-1 in exps) for (_,_,exps) in relations)
    col_list = []
    if have_minus1:
        col_list.append(-1)
    col_list.extend(fb)
    col_index = {p:i for i,p in enumerate(col_list)}
    rows_bits = []
    for (a,Q,exps) in relations:
        bitmask = 0
        for p,e in exps.items():
            if p not in col_index:
                continue
            idx = col_index[p]
            if e % 2 == 1:
                bitmask |= (1 << idx)
        rows_bits.append(bitmask)
    return rows_bits, col_list

def gaussian_elimination_rows_tracking(rows_bits, ncols):
    """
    Gaussian elimination mod 2 on rows represented by integers.
    Returns list of dependency masks (bitmask over rows).
    """
    rows = rows_bits[:]  # copy
    m = len(rows)
    T = [(1 << i) for i in range(m)]
    pivot_row_for_col = {}
    row_idx = 0
    for col in range(ncols):
        sel = None
        for r in range(row_idx, m):
            if (rows[r] >> col) & 1:
                sel = r
                break
        if sel is None:
            continue
        if sel != row_idx:
            rows[sel], rows[row_idx] = rows[row_idx], rows[sel]
            T[sel], T[row_idx] = T[row_idx], T[sel]
        pivot_row_for_col[col] = row_idx
        for r in range(0, m):
            if r != row_idx and ((rows[r] >> col) & 1):
                rows[r] ^= rows[row_idx]
                T[r] ^= T[row_idx]
        row_idx += 1
        if row_idx >= m:
            break
    deps = []
    for r in range(m):
        if rows[r] == 0:
            deps.append(T[r])
    return deps

# ---------------- Combine relations into X and Y ----------------

def combine_relations_from_bitmask(bitmask, relations, col_list, n):
    total_exps = defaultdict(int)
    X = 1 % n
    for i in range(len(relations)):
        if (bitmask >> i) & 1:
            a, Q, exps = relations[i]
            X = (X * (a % n)) % n
            for p,e in exps.items():
                total_exps[p] += e
    Y = 1 % n
    for p, e in total_exps.items():
        if p == -1:
            half = e // 2
            if half % 2 == 1:
                Y = (-Y) % n
            continue
        half = e // 2
        if half > 0:
            Y = (Y * pow(p, half, n)) % n
    return X % n, Y % n

# ---------------- Quadratic Sieve main ----------------

def quadratic_sieve(n, B=None, M=None, max_rel=None, verbose=True, collect_stats=False):
    """
    Quadratic Sieve main function.
    If collect_stats=True returns (p, stats_dict) else returns p (or None).
    """
    t_start = time.perf_counter() if 'time' in globals() else time.time()

    if n % 2 == 0:
        if collect_stats:
            return 2, {"quick": True}
        return 2
    if is_square(n):
        s = isqrt(n)
        if collect_stats:
            return s, {"quick": True}
        return s

    # heuristics for B and M (improved for ~64-bit and above)
    ln = math.log(n)
    if B is None:
        # coefficient tuned experimentally for moderate sizes
        B = int(exp(0.56 * math.sqrt(ln * math.log(ln)))) if n > 10 else 100
        B = max(5000, min(B, 50000))
    fb = build_factor_base(n, B)
    if verbose:
        print(f"[+] n={n}")
        print(f"[+] factor base bound B={B} -> fb size={len(fb)}")

    if M is None:
        M = int(B * 40)  # larger sieving interval to find enough smooths
    if verbose:
        print(f"[+] sieving interval M = {M} (will sieve 2M+1 values around sqrt(n))")

    required = max_rel if max_rel is not None else (len(fb) + 30)
    if verbose:
        print(f"[+] aiming for {required} relations (fb size + margin)")

    relations = []
    a0 = isqrt(n)
    block_center = a0
    iterations = 0
    blocks_sieved = 0
    candidates_total = 0

    # adaptivity limits
    adaptive_tries = 0
    max_adaptive = 8

    while len(relations) < required:
        if verbose:
            print(f"[+] sieving block center a0={block_center} (relations so far: {len(relations)})")
        candidates = sieve_block(n, fb, M, block_center, log_threshold=1.8)
        blocks_sieved += 1
        candidates_total += len(candidates)
        if verbose:
            print(f"    found {len(candidates)} candidate(s) in this block")
        # append new candidates not duplicating a's
        existing_as = set(r[0] for r in relations)
        for cand in candidates:
            a, Q, exps = cand
            if a in existing_as:
                continue
            relations.append(cand)
            existing_as.add(a)
            if len(relations) >= required:
                break

        if len(candidates) == 0:
            # adaptively increase M and maybe B to escape starvation
            adaptive_tries += 1
            if adaptive_tries <= max_adaptive:
                oldM, oldB = M, B
                M = int(M * 1.5)
                B = int(B * 1.1)
                fb = build_factor_base(n, B)
                if verbose:
                    print(f"    [adaptive] increased M {oldM}->{M}, B {oldB}->{B}, fb_size={len(fb)}")
                # continue sieving at same block_center with larger window
                continue
            else:
                if verbose:
                    print("    [adaptive] reached max adaptive tries; proceeding with what we have.")
                break

        # move to next block (advance)
        block_center += 2*M + 1
        iterations += 1
        if iterations > 2000:
            if verbose:
                print("[!] reached maximum block iterations; stopping collection")
            break

    if verbose:
        print(f"[+] collected {len(relations)} relations (candidates_total={candidates_total}, blocks={blocks_sieved})")

    if len(relations) == 0:
        if verbose:
            print("[!] No relations collected; try increasing B or M manually.")
        if collect_stats:
            return None, {"relations": 0, "blocks": blocks_sieved, "B": B, "M": M}
        return None

    # build matrix
    rows_bits, col_list = build_matrix(relations, fb)
    ncols = len(col_list)
    if verbose:
        print(f"[+] matrix: rows={len(rows_bits)} cols={ncols} (including -1 if present)")

    # elimination
    deps = gaussian_elimination_rows_tracking(rows_bits, ncols)
    if verbose:
        print(f"[+] found {len(deps)} zero-row dependencies (candidates to try)")

    # try deps
    for dep_mask in deps:
        X, Y = combine_relations_from_bitmask(dep_mask, relations, col_list, n)
        g = gcd(X - Y, n)
        if 1 < g < n:
            if verbose:
                print(f"[+] nontrivial factor found: {g}")
            if collect_stats:
                stats = {
                    "B": B, "M": M, "fb_size": len(fb), "relations": len(relations),
                    "blocks": blocks_sieved, "deps_zero_rows": len(deps)
                }
                return g, stats
            return g

    # fallback: try xor combinations and random subsets
    combined_deps = list(deps)
    if len(deps) >= 2:
        for _ in range(min(200, len(deps) * 5)):
            i, j = random.sample(range(len(deps)), 2)
            combined_deps.append(deps[i] ^ deps[j])

    m = len(relations)
    if m >= 2:
        hi = min(m, max(5, ncols//2 if ncols > 0 else 5))
        if hi < 2:
            hi = 2
        for _ in range(400):
            k = random.randint(2, hi)
            bm = 0
            for idx in random.sample(range(m), k):
                bm ^= (1 << idx)
            combined_deps.append(bm)

    tried = set()
    for dep_mask in combined_deps:
        if dep_mask in tried:
            continue
        tried.add(dep_mask)
        X, Y = combine_relations_from_bitmask(dep_mask, relations, col_list, n)
        g = gcd(X - Y, n)
        if 1 < g < n:
            if verbose:
                print(f"[+] nontrivial factor found (random try): {g}")
            if collect_stats:
                stats = {
                    "B": B, "M": M, "fb_size": len(fb), "relations": len(relations),
                    "blocks": blocks_sieved, "deps_zero_rows": len(deps)
                }
                return g, stats
            return g

    if verbose:
        print("[!] Failed to find a factor. Try increasing B and/or M, collect more relations, enable large-prime strategies, or use optimized libraries.")

    if collect_stats:
        stats = {
            "B": B, "M": M, "fb_size": len(fb), "relations": len(relations),
            "blocks": blocks_sieved, "deps_zero_rows": len(deps)
        }
        return None, stats
    return None

# ---------------- Wrapper for RSABenchmark ----------------
# ---------------- Wrapper para RSABenchmark (CORRIGIDO) ----------------
def quadratic_sieve_attack(n, e=None, **kwargs):
    """
    Compatível com RSABenchmark.run, que chama attack_func(n, e, **attack_kwargs).
    Garante retornar (p, q, extra_dict).
    Aceita kwargs opcionais: verbose, B, M, max_rel.
    """
    verbose = kwargs.get("verbose", False)
    B = kwargs.get("B", None)
    M = kwargs.get("M", None)
    max_rel = kwargs.get("max_rel", None)

    # Peça stats para saber o que aconteceu internamente
    p_or_none = None
    stats = {}
    # quadratic_sieve pode retornar:
    # - p (int or None)  OR
    # - (p, stats_dict) quando collect_stats=True
    try:
        # se a sua função quadratic_sieve suporta collect_stats use-o:
        maybe = quadratic_sieve(n, B=B, M=M, max_rel=max_rel, verbose=verbose, collect_stats=True)
        # espera um par (p, stats) ou (None, stats)
        if isinstance(maybe, tuple) and len(maybe) == 2:
            p_or_none, stats = maybe
        else:
            # caso inesperado: pode ter retornado só p
            p_or_none = maybe
            stats = {}
    except TypeError:
        # fallback: chamar sem collect_stats se assinatura não suportar
        p_or_none = quadratic_sieve(n, B=B, M=M, max_rel=max_rel, verbose=verbose)
        stats = {}

    # tempo / extra: se o benchmark já mede o tempo, aqui apenas acrescentamos stats
    extra = {}
    extra.update(stats if isinstance(stats, dict) else {})

    if p_or_none is None:
        extra.setdefault("status", "fail")
        return None, None, extra

    p = int(p_or_none)
    if n % p != 0:
        # proteção: se por algum motivo p não divide n, erro
        extra.setdefault("status", "invalid_factor")
        extra.setdefault("note", "returned factor does not divide n")
        return None, None, extra

    q = n // p
    extra.setdefault("status", "ok")
    extra.setdefault("found_factor", p)
    extra.setdefault("cofactor", q)
    return p, q, extra

# Wrapper para integrar o Quadratic Sieve ao benchmark RSA
# ----------------------------------------------------------

# -------------------- EXEMPLO RSABenchmark -----------------------

if __name__ == "__main__":
    bench = RSABenchmark(
        key_sizes_bits=(64, 128, 256, 512, 1024),
        seed=42,
    )

    results = bench.run(
        quadratic_sieve_attack,
        verbose=True,        # agora não causa conflito
    )

    print(f"{'Bits':4} {'Sucesso':8} {'Tempo (s)':10} Extra")
    print("-" * 60)
    for r in results:
        print(
            f"{r.key_bits:4} "
            f"{str(r.success):8} "
            f"{r.elapsed_seconds:10.6f} "
            f"{r.extra}"
        )

    bench.print_final_report(results)
