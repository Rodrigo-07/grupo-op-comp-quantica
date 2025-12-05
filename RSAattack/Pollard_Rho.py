from BaseAttack import RSABenchmark
import math
import random


def pollard_rho_attack(
    n: int,
    e: int,
    c_start: int = None,
    x_start: int = 2,
    max_iter: int = 10_000_000,
    progress_interval: int = 1000,
):
    """
    Implementação do Pollard Rho (ρ), compatível com a interface do RSABenchmark.

    - Usa tartaruga e lebre (Floyd cycle finding)
    - Função padrão: f(x) = x^2 + c (mod n)
    - c é aleatório se não fornecido
    - Log de progresso igual ao Pollard p-1
    """

    # Evita casos triviais
    if n % 2 == 0:
        return (2, n // 2, {
            "status": "factor_found",
            "iters": 0,
            "x_final": x_start,
            "y_final": x_start,
            "c": c_start,
        })

    # c é constante aleatória se não especificada
    if c_start is None:
        c = random.randrange(1, n - 1)
    else:
        c = c_start

    # Tartaruga e lebre
    x = x_start
    y = x_start

    # Contador de iterações
    iters = 0

    # Função iteradora f(x)
    def f(z: int) -> int:
        return (z * z + c) % n

    while iters < max_iter:
        # Tartaruga: 1 passo
        x = f(x)

        # Lebre: 2 passos
        y = f(f(y))

        # d = gcd(|x - y|, n)
        d = math.gcd(abs(x - y), n)

        iters += 1

        # Log periódico
        if iters % progress_interval == 0:
            print(f"   [Pollard Rho] iters={iters}, gcd(x-y, n)={d}, c={c}")

        # caso encontrou fator não trivial
        if 1 < d < n:
            p = d
            q = n // d
            return (p, q, {
                "status": "factor_found",
                "iters": iters,
                "x_final": x,
                "y_final": y,
                "c": c,
            })

        # caso ciclo ruim: restart automático
        if d == n:
            # Reescolhe c e reinicia (prática comum)
            c = random.randrange(1, n - 1)
            x = x_start
            y = x_start

    # Chegou no limite sem fatorar
    return (None, None, {
        "status": "max_iter_reached",
        "iters": iters,
        "x_final": x,
        "y_final": y,
        "c": c,
    })


# -------------------- EXEMPLO RSABenchmark -----------------------

if __name__ == "__main__":
    bench = RSABenchmark(
        key_sizes_bits=(64, 128, 256, 512, 1024),
        seed=42,
    )

    results = bench.run(
        pollard_rho_attack,
        x_start=2,
        c_start=None,          # deixa c aleatório por rodada
        max_iter=10_000_000,
        progress_interval=2000,
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

