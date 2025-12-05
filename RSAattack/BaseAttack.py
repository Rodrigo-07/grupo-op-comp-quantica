import math
import random
import time
from dataclasses import dataclass
from typing import Callable, List, Any, Dict


@dataclass
class AttackResult:
    key_bits: int
    n: int
    success: bool
    p: int | None
    q: int | None
    elapsed_seconds: float
    extra: dict


class RSABenchmark:
    """
    Classe simples para:
      - gerar algumas chaves RSA pequenas
      - aplicar UMA função de ataque em todas as chaves
      - medir tempo e sucesso
    """

    def __init__(
        self,
        key_sizes_bits=(16, 20, 24, 28, 32),
        e: int = 65537,
        seed: int | None = None,
    ):
        self.key_sizes_bits = key_sizes_bits
        self.base_e = e

        if seed is not None:
            random.seed(seed)

        self.keys: List[Dict[str, Any]] = []
        self._generate_keys()

    # ------------------------------
    #  Geração de chaves pequenas
    # ------------------------------

    def _is_probable_prime(self, n: int, k: int = 8) -> bool:
        """Teste de primalidade Miller-Rabin (provável primo)."""
        if n < 2:
            return False
        small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        if n in small_primes:
            return True
        for p in small_primes:
            if n % p == 0:
                return False

        # escreve n-1 como 2^r * d
        d = n - 1
        r = 0
        while d % 2 == 0:
            d //= 2
            r += 1

        for _ in range(k):
            a = random.randrange(2, n - 2)
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        return True

    def _generate_prime(self, bits: int) -> int:
        """Gera um primo com aproximadamente 'bits' bits."""
        while True:
            candidate = random.getrandbits(bits)
            candidate |= (1 << (bits - 1))  # garante bit mais significativo = 1
            candidate |= 1                  # garante que é ímpar
            if self._is_probable_prime(candidate):
                return candidate

    def _generate_keys(self):
        """Gera as chaves RSA para todos os tamanhos especificados."""
        for bits in self.key_sizes_bits:
            half = bits // 2
            p = self._generate_prime(half)
            q = self._generate_prime(bits - half)

            n = p * q
            phi = (p - 1) * (q - 1)

            e = self.base_e
            while math.gcd(e, phi) != 1:
                e += 2

            d = pow(e, -1, phi)

            self.keys.append(
                {
                    "bits": bits,
                    "p": p,
                    "q": q,
                    "n": n,
                    "phi": phi,
                    "e": e,
                    "d": d,
                }
            )

    # ------------------------------
    #  Rodar UMA função de ataque
    # ------------------------------

    def run(
        self,
        attack_func: Callable[..., Any],
        **attack_kwargs,
    ) -> List[AttackResult]:
        """
        Aplica attack_func em todas as chaves.

        A função deve ter assinatura compatível com:
            attack_func(n: int, e: int, **opcionais)

        E deve devolver, OBRIGATORIAMENTE:
            - uma tupla: (p, q) ou (p, q, ...extras...)
            - ou um dict com 'p' e 'q' (e outras chaves opcionais)
        """
        results: List[AttackResult] = []

        for key in self.keys:
            n = key["n"]
            e = key["e"]
            bits = key["bits"]

            start = time.perf_counter()
            extra: dict = {}
            p = q = None

            try:
                out = attack_func(n, e, **attack_kwargs)
            except Exception as ex:
                elapsed = time.perf_counter() - start
                results.append(
                    AttackResult(
                        key_bits=bits,
                        n=n,
                        success=False,
                        p=None,
                        q=None,
                        elapsed_seconds=elapsed,
                        extra={"error": str(ex)},
                    )
                )
                continue

            elapsed = time.perf_counter() - start

            # trata saída
            if isinstance(out, tuple):
                if len(out) >= 2:
                    p, q = out[0], out[1]
                    if len(out) > 2:
                        extra["rest"] = out[2:]
            elif isinstance(out, dict):
                p = out.get("p")
                q = out.get("q")
                extra = {k: v for k, v in out.items() if k not in ("p", "q")}
            else:
                extra["error"] = "Saída inválida do ataque (use tuple ou dict)"

            success = p is not None and q is not None and (p * q == n)

            results.append(
                AttackResult(
                    key_bits=bits,
                    n=n,
                    success=success,
                    p=p if success else None,
                    q=q if success else None,
                    elapsed_seconds=elapsed,
                    extra=extra,
                )
            )

        return results


# ===========================================
# Exemplo de função de ataque: trial division
# ===========================================

def trial_division_attack(n: int, e: int, limit_factor: float = 1.0):
    """
    Exemplo simples: tenta dividir n por todos os inteiros até sqrt(n)*limit_factor.

    Retorna (p, q, steps) para mostrar exemplo de extras.
    """
    limit = int(math.isqrt(n) * limit_factor)
    steps = 0
    for d in range(2, limit + 1):
        steps += 1
        if n % d == 0:
            p = d
            q = n // d
            return (p, q, {"steps": steps})
    return (None, None, {"steps": steps})


# ============================
# Exemplo de uso / "main"
# ============================
if __name__ == "__main__":
    bench = RSABenchmark(
        key_sizes_bits=(16, 20, 24, 28, 32),
        seed=42,
    )

    results = bench.run(trial_division_attack, limit_factor=1.0)

    print(f"{'Bits':4} {'Sucesso':8} {'Tempo (s)':10} Extra")
    print("-" * 60)
    for r in results:
        print(
            f"{r.key_bits:4} "
            f"{str(r.success):8} "
            f"{r.elapsed_seconds:10.6f} "
            f"{r.extra}"
        )
