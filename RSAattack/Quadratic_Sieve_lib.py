from BaseAttack import RSABenchmark
from quadratic_sieve.quadratic_sieve import factorize
def quadratic_sieve_attack(n, e=None, **kwargs):
    """
    Wrapper compatível com RSABenchmark.run.
    Usa o factorize da lib quadratic_sieve
    """
    verbose = kwargs.get("verbose", False)
    extra = {}

    try:
        factors = factorize(n)   # {p: exp, q: exp, ...}
    except Exception as exc:
        extra["status"] = "error"
        extra["exception"] = str(exc)
        return None, None, extra

    # substituir casos em que não fatorou
    if len(factors) < 2:
        extra["status"] = "fail"
        extra["factors"] = factors
        return None, None, extra

    # extrair primeiros dois fatores
    p , q  = factors

    extra["status"] = "ok"
    extra["method"] = "quadratic_sieve.factorize"
    extra["factors"] = factors

    return int(p), int(q), extra


# -------------------- EXEMPLO RSABenchmark -----------------------
if __name__ == "__main__":
    bench = RSABenchmark(
        key_sizes_bits=(64, 128, 256, 512, 1024),
        seed=42,
    )

    results = bench.run(
        quadratic_sieve_attack,
        verbose=True,
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
