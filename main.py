import math


def show_banner():
    print("=" * 60)
    print("""
██╗      ██████╗ ████████╗ ██████╗ ███████╗ █████╗  ██████╗ ██╗██╗     
██║     ██╔═══██╗╚══██╔══╝██╔═══██╗██╔════╝██╔══██╗██╔════╝ ██║██║     
██║     ██║   ██║   ██║   ██║   ██║█████╗  ███████║██║      ██║██║     
██║     ██║   ██║   ██║   ██║   ██║██╔══╝  ██╔══██║██║      ██║██║     
███████╗╚██████╔╝   ██║   ╚██████╔╝██║     ██║  ██║╚██████╗ ██║███████╗
╚══════╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝╚══════╝
    """)
    print("Lotofácil Combination Calculator")
    print("Calcule quantas apostas simples seu jogo equivale")
    print("=" * 60)
    print()


def calculate_equivalent_bets(numbers_selected: int, number_of_bets: int) -> int:
    if numbers_selected < 15:
        raise ValueError("numbers_selected must be at least 15")

    return math.comb(numbers_selected, 15) * number_of_bets


def main():
    show_banner()

    numbers_selected = int(input("Quantidade de dezenas: "))
    number_of_bets = int(input("Quantidade de jogos: "))

    equivalent_bets = calculate_equivalent_bets(numbers_selected, number_of_bets)

    print()
    print("-" * 60)
    print(f"Jogadas equivalentes (15 dezenas): {equivalent_bets}")
    print("-" * 60)


if __name__ == "__main__":
    main()
