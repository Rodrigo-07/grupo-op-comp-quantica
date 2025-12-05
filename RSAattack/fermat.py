import math
from typing import Optional, Tuple

def fermat_factor(n: int, max_iters: Optional[int] = None) -> Optional[Tuple[int,int]]:
    
    if n <= 1:
        return None

    if n % 2 == 0:
        return 2, n // 2

    a = math.isqrt(n)
    if a * a < n:
        a += 1

    it = 0
    while True:
        b2 = a*a - n
        if b2 < 0:
            a += 1
            it += 1
            if max_iters and it > max_iters:
                return None
            continue

        b = math.isqrt(b2)
        if b*b == b2:
            p = a - b
            q = a + b
            if 1 < p < n and 1 < q < n:
                return (p, q) if p <= q else (q, p)
            return None

        a += 1
        it += 1
        if max_iters and it > max_iters:
            return None
