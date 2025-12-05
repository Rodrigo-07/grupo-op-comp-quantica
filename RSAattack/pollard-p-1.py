from BaseAttack import RSABenchmark
import math

def pollard_p_minus_1_attack(
    n: int,
    e: int,
    a_start: int = 2,
    max_iter: int = 100000,
    progress_interval: int = 1000,
):
    """
    Ataque Pollard p-1 (versão simples, estilo GeeksforGeeks),
    adaptado para a interface do RSABenchmark.
    """
    a = a_start
    i = 2
    iters = 0

    while iters < max_iter:
        # a <- a^i (mod n)
        a = pow(a, i, n)

        # d = gcd(a-1, n)
        d = math.gcd(a - 1, n)

        iters += 1

        # log periódico opcional
        if iters % progress_interval == 0:
            print(f"   [Pollard p-1] iters={iters}, i={i}, gcd(a-1, n)={d}")

        # se achou fator não trivial
        if 1 < d < n:
            p = d
            q = n // d
            return (p, q, {
                "iters": iters,
                "i_final": i,
                "a_final": a,
                "status": "factor_found",
            })

        i += 1

    # se chegou aqui, não conseguiu fatorar com esses parâmetros
    return (None, None, {
        "iters": iters,
        "i_final": i - 1,
        "a_final": a,
        "status": "max_iter_reached",
    })


if __name__ == "__main__":
    bench = RSABenchmark(
        key_sizes_bits=(16, 20, 24, 28, 2048),
        seed=42,
    )

    results = bench.run(
        pollard_p_minus_1_attack,
        a_start=2,
        max_iter=100000,
        progress_interval=1000,
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
