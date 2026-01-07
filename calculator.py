import math
import os

VALOR_APOSTA_SIMPLES = 3.50
MIN_DEZENAS = 15
MAX_DEZENAS = 20
MIN_JOGOS = 1

TOTAL_NUMEROS = 25
NUMEROS_SORTEADOS = 15

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

def format_currency(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_int_br(value: int) -> str:
    return f"{value:,}".replace(",", ".")

def format_float_br(value: float, decimals: int = 1) -> str:
    s = f"{value:,.{decimals}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

def format_odds_from_p(p: float) -> str:
    if p <= 0.0:
        return "—"

    odds = 1.0 / p
    rounded = round(odds)
    if abs(odds - rounded) < 1e-9:
        return f"1 em {format_int_br(int(rounded))}"

    return f"1 em {format_float_br(odds, 1)}"

def calculate_equivalent_bets(numbers_selected: int, number_of_bets: int) -> int:
    return math.comb(numbers_selected, 15) * number_of_bets

def hypergeom_p(n_chosen: int, hits: int) -> float:
    if hits < 0:
        return 0.0
    if hits > n_chosen or hits > NUMEROS_SORTEADOS:
        return 0.0

    remaining = TOTAL_NUMEROS - n_chosen
    misses_needed = NUMEROS_SORTEADOS - hits
    if misses_needed < 0 or misses_needed > remaining:
        return 0.0

    num = math.comb(n_chosen, hits) * math.comb(remaining, misses_needed)
    den = math.comb(TOTAL_NUMEROS, NUMEROS_SORTEADOS)
    return num / den

def p_at_least_one(p_single: float, trials: int) -> float:
    if trials <= 0:
        return 0.0
    if p_single <= 0.0:
        return 0.0
    if p_single >= 1.0:
        return 1.0
    return 1.0 - math.exp(trials * math.log1p(-p_single))

def format_table(headers: list[str], rows: list[list[str]]) -> str:
    col_count = len(headers)
    widths = [len(h) for h in headers]
    for r in rows:
        for i in range(col_count):
            widths[i] = max(widths[i], len(r[i]))

    def border(left: str, mid: str, right: str) -> str:
        pieces = []
        for w in widths:
            pieces.append("─" * (w + 2))
        return left + mid.join(pieces) + right

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

def run_once() -> None:
    numbers_selected = get_valid_int("Quantidade de dezenas (15 a 20): ", MIN_DEZENAS, MAX_DEZENAS)
    number_of_bets = get_valid_int("Quantidade de jogos: ", MIN_JOGOS)

    equivalent_bets = calculate_equivalent_bets(numbers_selected, number_of_bets)
    total_cost = equivalent_bets * VALOR_APOSTA_SIMPLES

    print()

    headers = ["Faixa", "1 jogo", f"{format_int_br(number_of_bets)} jogos (>=1)*"]
    prob_rows: list[list[str]] = []

    for hits in [15, 14, 13, 12, 11]:
        p1 = hypergeom_p(numbers_selected, hits)
        pn = p_at_least_one(p1, number_of_bets)
        faixa = "15 acertos (prêmio principal)" if hits == 15 else f"{hits} acertos"
        prob_rows.append([faixa, format_odds_from_p(p1), f"{format_odds_from_p(pn)}  ({format_float_br(pn * 100, 4)}%)"])

    print("Probabilidades:")
    print(format_table(headers, prob_rows))
    print()
    print("*Assumindo jogos diferentes/independentes. Repetir o mesmo jogo não aumenta a chance.")
    print()

    result_headers = ["Descrição", "Valor"]
    result_rows = [
        ["Dezenas por jogo", str(numbers_selected)],
        ["Quantidade de jogos", format_int_br(number_of_bets)],
        ["Apostas simples equivalentes", format_int_br(equivalent_bets)],
        ["Valor total a pagar", format_currency(total_cost)],
    ]

    print("Resultado:")
    print(format_table(result_headers, result_rows))
    print()

def run() -> None:
    while True:
        run_once()
        choice = input("Enter para novo cálculo | 'q' para voltar ao menu: ").strip().lower()
        if choice in {"q", "quit", "sair", "exit"}:
            break
