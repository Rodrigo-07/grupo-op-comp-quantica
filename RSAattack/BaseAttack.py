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
    Classe para:
    - gerar chaves RSA pequenas
    - aplicar UMA função de ataque
    - mostrar logs detalhados
    - gerar relatório final
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
        if n < 2:
            return False
        small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        if n in small_primes:
            return True
        for p in small_primes:
            if n % p == 0:
                return False

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
        while True:
            candidate = random.getrandbits(bits)
            candidate |= (1 << (bits - 1))
            candidate |= 1
            if self._is_probable_prime(candidate):
                return candidate

    def _generate_keys(self):
        print("\n🔐 Gerando chaves RSA...\n")
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

            print(f" - Chave {bits:2} bits gerada: n = {n}")

            self.keys.append(
                {"bits": bits, "p": p, "q": q, "n": n, "phi": phi, "e": e, "d": d}
            )

        print("\n✅ Todas as chaves foram geradas!\n")

    # ------------------------------
    #  Rodar ataque com logs detalhados
    # ------------------------------

    def run(self, attack_func: Callable[..., Any], **attack_kwargs) -> List[AttackResult]:
        results: List[AttackResult] = []

        print("\n🚀 Iniciando ataques...\n")

        for key in self.keys:
            n, e, bits = key["n"], key["e"], key["bits"]

            print(f"\n==========================================")
            print(f"🔎 Rodando teste com chave de {bits} bits")
            print(f"   n = {n}")
            print(f"==========================================\n")

            start = time.perf_counter()
            extra: dict = {}
            p = q = None

            try:
                out = attack_func(n, e, **attack_kwargs)
            except KeyboardInterrupt:
                elapsed = time.perf_counter() - start
                print("⏹ Execução interrompida pelo usuário (Ctrl+C) durante este ataque.\n")

                # registra essa chave como interrompida
                results.append(
                    AttackResult(
                        bits,
                        n,
                        False,
                        None,
                        None,
                        elapsed,
                        {"interrupted": True},
                    )
                )

                print("⚠ Interrupção detectada. Gerando relatório parcial com os resultados até agora...\n")
                break  # sai do loop de chaves e retorna resultados parciais

            except Exception as ex:
                elapsed = time.perf_counter() - start
                print(f"❌ ERRO no ataque: {ex}\n")
                results.append(
                    AttackResult(bits, n, False, None, None, elapsed, {"error": str(ex)})
                )
                continue

            elapsed = time.perf_counter() - start

            # trata saída
            if isinstance(out, tuple):
                p, q = out[0], out[1]
                if len(out) > 2:
                    third = out[2]
                    if isinstance(third, dict):
                        extra.update(third)
                    else:
                        extra["rest"] = third
            elif isinstance(out, dict):
                p = out.get("p")
                q = out.get("q")
                extra = {k: v for k, v in out.items() if k not in ("p", "q")}

            success = p is not None and q is not None and p * q == n

            if success:
                print("✔ Sucesso! Fatores encontrados:")
                print(f"   p = {p}")
                print(f"   q = {q}")
            else:
                print("❌ Falha: ataque não encontrou p e q.")

            print(f"⏱ Tempo total: {elapsed:.6f} segundos")
            print(f"📊 Extra: {extra}")
            print()

            results.append(
                AttackResult(bits, n, success, p if success else None, q if success else None, elapsed, extra)
            )

        print("\n🏁 Fim dos ataques (normal ou interrompido)!\n")
        return results

    # ------------------------------
    #  Relatório final (agora método)
    # ------------------------------

    def print_final_report(self, results: List[AttackResult]) -> None:
        print("\n================ RELATÓRIO FINAL ================\n")

        total = len(results)
        success_count = sum(1 for r in results if r.success)
        fail_count = total - success_count
        success_rate = (success_count / total * 100) if total > 0 else 0.0

        print(f"Total de chaves testadas (inclui interrompidas): {total}")
        print(f"Quebradas com sucesso                          : {success_count}")
        print(f"Falharam / não quebradas                       : {fail_count}")
        print(f"Taxa de sucesso                                : {success_rate:.2f}%\n")

        # Agrupar por tamanho de chave
        stats: Dict[int, List[AttackResult]] = {}
        for r in results:
            stats.setdefault(r.key_bits, []).append(r)

        print("Resumo por tamanho de chave:\n")
        print(f"{'Bits':4} {'#Total':6} {'#OK':4} {'Sucesso%':9} {'t_med (s)':10} {'steps_med':10}")
        print("-" * 60)

        for bits, group in sorted(stats.items()):
            total_b = len(group)
            ok_b = sum(1 for r in group if r.success)
            rate_b = (ok_b / total_b * 100) if total_b > 0 else 0.0
            avg_time = sum(r.elapsed_seconds for r in group) / total_b if total_b > 0 else 0.0

            steps_list = []
            for r in group:
                steps = r.extra.get("steps")
                if isinstance(steps, (int, float)):
                    steps_list.append(steps)
            avg_steps = sum(steps_list) / len(steps_list) if steps_list else 0.0

            print(
                f"{bits:4} "
                f"{total_b:6} "
                f"{ok_b:4} "
                f"{rate_b:9.2f} "
                f"{avg_time:10.6f} "
                f"{avg_steps:10.2f}"
            )

        print("\n=================================================\n")

