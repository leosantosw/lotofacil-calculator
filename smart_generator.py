import time
import random
import requests
from collections import Counter

BASE = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"
TOTAL_NUMEROS = 25

MIN_CONCURSOS = 10
MAX_CONCURSOS = 1000

TOP_MOST_SORTED = 10


def get_valid_int(prompt: str, min_value: int, max_value: int | None = None) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("❌ Entrada inválida. Digite apenas números inteiros.")
            continue

        if value < min_value:
            print(f"❌ Valor mínimo permitido: {min_value}")
            continue

        if max_value is not None and value > max_value:
            print(f"❌ Valor máximo permitido: {max_value}")
            continue

        return value


def fetch_json(url: str, session: requests.Session) -> dict:
    r = session.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    return r.json()


def fetch_last_results(last_n: int, delay_s: float = 0.15) -> list[dict]:
    with requests.Session() as session:
        latest = fetch_json(BASE, session)
        latest_number = int(latest["numero"])

        results: list[dict] = []
        n = latest_number

        while len(results) < last_n and n > 0:
            try:
                data = fetch_json(f"{BASE}/{n}", session)
                results.append(data)
            except requests.RequestException:
                pass

            n -= 1
            time.sleep(delay_s)

        return results


def to_int_set(lista_dezenas) -> set[int]:
    out: set[int] = set()
    for d in (lista_dezenas or []):
        try:
            out.add(int(d))
        except (TypeError, ValueError):
            continue
    return out


def plural_concurso(x: int) -> str:
    return "concurso" if x == 1 else "concursos"


def format_table(headers: list[str], rows: list[list[str]]) -> str:
    col_count = len(headers)
    widths = [len(h) for h in headers]
    for r in rows:
        for i in range(col_count):
            widths[i] = max(widths[i], len(r[i]))

    def border(left: str, mid: str, right: str) -> str:
        return left + mid.join("─" * (w + 2) for w in widths) + right

    out = []
    out.append(border("┌", "┬", "┐"))
    out.append("│ " + " │ ".join(f"{headers[i]:<{widths[i]}}" for i in range(col_count)) + " │")
    out.append(border("├", "┼", "┤"))
    for idx, r in enumerate(rows):
        out.append("│ " + " │ ".join(f"{r[i]:<{widths[i]}}" for i in range(col_count)) + " │")
        if idx < len(rows) - 1:
            out.append(border("├", "┼", "┤"))
    out.append(border("└", "┴", "┘"))
    return "\n".join(out)


def compute_delays(last_results: list[dict]) -> dict[int, int | None]:
    draws = [to_int_set(r.get("listaDezenas")) for r in last_results]  # idx 0 = mais recente

    delays: dict[int, int | None] = {}
    for n in range(1, TOTAL_NUMEROS + 1):
        delay = None
        for idx, dezenas in enumerate(draws):
            if n in dezenas:
                delay = idx
                break
        delays[n] = delay

    return delays


def compute_counts(last_results: list[dict]) -> Counter:
    counter = Counter()
    for r in last_results:
        counter.update(to_int_set(r.get("listaDezenas")))
    for n in range(1, TOTAL_NUMEROS + 1):
        counter.setdefault(n, 0)
    return counter


def build_weights(delays: dict[int, int | None], counts: Counter, last_n: int) -> dict[int, float]:
    delay_vals = [(last_n + 1 if delays[n] is None else delays[n]) for n in range(1, TOTAL_NUMEROS + 1)]
    count_vals = [counts[n] for n in range(1, TOTAL_NUMEROS + 1)]

    dmin, dmax = min(delay_vals), max(delay_vals)
    cmin, cmax = min(count_vals), max(count_vals)

    def norm(x: float, a: float, b: float) -> float:
        if b == a:
            return 0.5
        return (x - a) / (b - a)

    weights: dict[int, float] = {}
    for n in range(1, TOTAL_NUMEROS + 1):
        d = last_n + 1 if delays[n] is None else delays[n]
        c = counts[n]

        delay_norm = norm(d, dmin, dmax)
        freq_norm = norm(c, cmin, cmax)

        score = 0.65 * delay_norm + 0.35 * (1.0 - freq_norm)
        weights[n] = 0.05 + score

    return weights


def weighted_sample_without_replacement(items: list[int], weights: list[float], k: int) -> list[int]:
    chosen: list[int] = []
    pool_items = items[:]
    pool_weights = weights[:]

    for _ in range(k):
        total = sum(pool_weights)
        r = random.random() * total
        acc = 0.0
        idx = 0
        for i, w in enumerate(pool_weights):
            acc += w
            if acc >= r:
                idx = i
                break

        chosen.append(pool_items.pop(idx))
        pool_weights.pop(idx)

    return chosen


def generate_games(num_games: int, dezenas_per_game: int, weights_by_number: dict[int, float]) -> list[list[int]]:
    items = list(range(1, TOTAL_NUMEROS + 1))
    weights = [weights_by_number[n] for n in items]

    games: list[list[int]] = []
    seen = set()

    attempts = 0
    while len(games) < num_games and attempts < num_games * 50:
        attempts += 1
        pick = weighted_sample_without_replacement(items, weights, dezenas_per_game)
        key = tuple(sorted(pick))
        if key in seen:
            continue
        seen.add(key)
        games.append(list(key))

    return games


def show_tables(last_results: list[dict]) -> tuple[dict[int, int | None], Counter]:
    delays = compute_delays(last_results)
    counts = compute_counts(last_results)

    filtered = [(d, a) for d, a in delays.items() if a is None or a >= 1]

    def delay_sort_key(item: tuple[int, int | None]):
        dez, atraso = item
        return (10**9 if atraso is None else atraso, dez)

    delayed_ordered = sorted(filtered, key=delay_sort_key, reverse=True)

    delayed_rows: list[list[str]] = []
    for dezena, atraso in delayed_ordered:
        if atraso is None:
            status = f"Não saiu nos últimos {len(last_results)} concursos"
        else:
            status = f"Não sai há {atraso} {plural_concurso(atraso)}"
        delayed_rows.append([f"{dezena:02d}", status])

    print("Números mais atrasados")
    print(format_table(["Dezena", "Status"], delayed_rows))
    print()

    most = sorted(counts.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)[:TOP_MOST_SORTED]
    most_rows = [[f"{dez:02d}", str(vezes)] for dez, vezes in most]

    print(f"Números mais sorteados (últimos {len(last_results)})")
    print(format_table(["Dezena", "Saiu (vezes)"], most_rows))
    print()

    return delays, counts


def run() -> None:
    contests_to_fetch = get_valid_int(
        f"Quantos concursos buscar? ({MIN_CONCURSOS} a {MAX_CONCURSOS}): ",
        MIN_CONCURSOS,
        MAX_CONCURSOS,
    )

    print(f"🔎 Buscando os últimos {contests_to_fetch} concursos... isso pode demorar um pouco.\n")
    last_results = fetch_last_results(last_n=contests_to_fetch)
    if not last_results:
        print("❌ Não consegui obter resultados da API.")
        input("Enter para voltar...")
        return

    last_n = len(last_results)

    while True:
        print(f"1) Mostrar atrasados + mais sorteados (últimos {last_n})")
        print(f"2) Gerar jogos (baseado nos últimos {last_n})")
        print("3) Voltar ao menu")
        print()
        opt = input("Escolha: ").strip()

        if opt == "3":
            break

        if opt not in {"1", "2"}:
            print("❌ Opção inválida.\n")
            continue

        delays, counts = show_tables(last_results)

        if opt == "2":
            num_games = get_valid_int("Gerar quantos jogos? ", 1, 500)
            dezenas = get_valid_int("Quantas dezenas por jogo (15 a 20)? ", 15, 20)

            weights = build_weights(delays, counts, last_n=last_n)
            games = generate_games(num_games, dezenas, weights)

            rows = [[str(i), " ".join(f"{n:02d}" for n in g)] for i, g in enumerate(games, start=1)]
            print("\nJogos gerados (heurística)")
            print(format_table(["#", "Dezenas"], rows))
            print()

        input("Enter para continuar...\n")
