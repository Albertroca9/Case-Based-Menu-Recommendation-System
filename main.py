# main.py

# Historial + Autocompletació (readline)
try:
    import readline
except ImportError:
    readline = None

# Imports
import os
import atexit
from data.carrega_dades import df_plats
from recomanador.recom import (obtenir_preferencies, recomanar_menu, imprimir_recomanacio, gestionar_post_recomanacio, imprimir_top3, seleccionar_menu_i_adaptar, imprimir_resum_general_menus)
from utils.helpers import BOLD, RESET, check_reset, check_exit
from cbr.forget import forget_cases_based_on_time
from cbr.usage import registrar_us

HISTORY_FILE = os.path.expanduser("~/.ricorico_history")

# Carregar Historial
if readline:
    if os.path.exists(HISTORY_FILE):
        try:
            readline.read_history_file(HISTORY_FILE)
        except Exception:
            pass

    def guardar_historial():
        try:
            readline.write_history_file(HISTORY_FILE)
        except Exception:
            pass

    atexit.register(guardar_historial)

# Programa principal
if __name__ == "__main__":

    while True:

        # Missatge de benvinguda
        print(f"\n{BOLD}RicoRico – Assistent de Menús Personalitzats{RESET}")
        print("-" * 66)
        print("Benvingut/da a RicoRico – el teu assistent per crear menús a mida!")
        print("Et farem unes preguntes inicials per adaptar el servei culinari")
        print("al tipus d’esdeveniment, estil i necessitats dels teus comensals.")
        print("Pots escriure «exit», «quit» o «reset» en qualsevol moment.")
        print("-" * 66 + "\n")

        # Obtenir preferències
        preferencies = obtenir_preferencies()
        if preferencies == "__RESTART_ALL__":
            continue

        # Recomanació automàtica
        recom = recomanar_menu(preferencies)

        # Registrar ús dels menús recomanats
        for cas, _ in recom["top3_adults"]:
            registrar_us(cas.menu_id)

        for cas, _ in recom["top3_infantil"]:
            registrar_us(cas.menu_id)

        # Mostrar resultats
        imprimir_top3(recom, preferencies, df_plats)
        imprimir_recomanacio(recom, preferencies, df_plats)
        imprimir_resum_general_menus(recom["top3_adults"], recom["top3_infantil"])

        # Forget (basat en temps)
        forget_cases_based_on_time(preferencies)

        # Fase d'adaptació
        cas_adults     = recom["cas_adults"]
        cas_infantil   = recom["cas_infantil"]
        top3_adults    = recom["top3_adults"]
        top3_infantil  = recom["top3_infantil"]

        while True:

            result = gestionar_post_recomanacio(
                cas_adults,
                cas_infantil,
                preferencies,
                top3_adults,
                top3_infantil
            )

            if result == "__RESTART_ALL__":
                break

            if result == "__BACK_TO_ADAPTATIONS__":
                continue

            if result == "__SELECT_ANOTHER_MENU__":

                while True:
                    result2 = seleccionar_menu_i_adaptar(
                        top3_adults,
                        top3_infantil,
                        preferencies
                    )

                    if result2 == "__RESTART_ALL__":
                        break

                    if result2 == "__SELECT_ANOTHER_MENU__":
                        continue

                    # None → sortida normal
                    break

                if result2 == "__RESTART_ALL__":
                    break

                print("\nVols iniciar un nou recomanador? (Si/No)")
                r = input("  >> ").strip().lower()

                if check_exit(r) or check_reset(r) or r.startswith("s"):
                    break

                print("Gràcies per utilitzar RicoRico!\n")
                exit(0)

            if result == "__FINISHED_SUCCESS__":
                print("\nGràcies per utilitzar RicoRico!\n")
                break

            # result == None → final normal de l’adaptació
            break

        # Reinici/sortida final
        print("\nVols iniciar un nou recomanador? (Si/No)")
        r = input("  >> ").strip().lower()

        if check_exit(r) or check_reset(r) or r.startswith("s"):
            continue

        print("Gràcies per utilitzar RicoRico!\n")
        break
