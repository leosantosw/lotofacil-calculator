import os
import calculator
import smart_generator

def show_banner() -> None:
    print("=" * 70)
    print(r"""
██╗      ██████╗ ████████╗ ██████╗ ███████╗ █████╗  ██████╗ ██╗██╗     
██║     ██╔═══██╗╚══██╔══╝██╔═══██╗██╔════╝██╔══██╗██╔════╝ ██║██║     
██║     ██║   ██║   ██║   ██║   ██║█████╗  ███████║██║      ██║██║     
██║     ██║   ██║   ██║   ██║   ██║██╔══╝  ██╔══██║██║      ██║██║     
███████╗╚██████╔╝   ██║   ╚██████╔╝██║     ██║  ██║╚██████╗ ██║███████╗
╚══════╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝     ╚═╝  ╚═╝ ╚══════╝ ╚═╝╚══════╝
    """)
    print("=" * 70)
    print()

def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")

def main() -> None:
    while True:
        clear_screen()
        show_banner()
        print("1) Calculadora (equivalência + probabilidades)")
        print("2) Análise de resultados + gerador")
        print("3) Sair")
        print()

        choice = input("Escolha: ").strip()

        if choice == "1":
            calculator.run()
        elif choice == "2":
            smart_generator.run()
        elif choice == "3":
            print("\n👋 Valeu!\n")
            break
        else:
            input("❌ Opção inválida. Enter para tentar de novo...")

if __name__ == "__main__":
    main()
