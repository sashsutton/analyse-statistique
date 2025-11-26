import os
import glob
import numpy as np
import pandas as pd
from scipy import stats  # Nécessaire pour la loi de Student
# On réutilise la fonction de calcul unitaire existante
from global_sigma_analysis import calculate_intra_sample_global_sigma

# --- CONFIGURATION ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "batch")

# Paramètres définis dans votre document (Screenshot)
SEUIL_TOLERABLE_MICRONS = 20.0  # 20 µm
ALPHA = 0.05  # Risque 5%


def run_statistical_test():
    """
    Exécute le Test t de Student unilatéral et calcule l'IC.
    H0: Reproducibilité >= 20 µm (Mauvais)
    H1: Reproducibilité < 20 µm (Bon)
    """

    # 1. Collecte des données (Sigma_k) pour chaque patient
    batch_folders = sorted(glob.glob(os.path.join(DATA_DIR, "batch_*")))
    sigma_k_microns_list = []

    print(f"--- COLLECTE DES DONNÉES (N={len(batch_folders)}) ---")

    for folder in batch_folders:
        batch_id = os.path.basename(folder).split('_')[-1]

        # On appelle le calcul (mode silencieux)
        result = calculate_intra_sample_global_sigma(batch_id, verbose=False)

        if result is not None:
            sigma_k_mm, _ = result
            # CONVERSION CRUCIALE EN MICRONS
            sigma_k_um = sigma_k_mm * 1000.0
            sigma_k_microns_list.append(sigma_k_um)
            print(f"  Batch {batch_id} : {sigma_k_um:.3f} µm")
        else:
            print(f"  Batch {batch_id} : Ignoré (Données insuffisantes)")

    # 2. Vérification de la taille de l'échantillon
    N = len(sigma_k_microns_list)
    if N < 2:
        print("\n[ERREUR] Impossible de faire un test de Student avec moins de 2 patients.")
        return

    # 3. Calculs Statistiques (D'après vos formules manuscrites)
    data = np.array(sigma_k_microns_list)

    # Moyenne (Sigma_global)
    mean_global = np.mean(data)

    # Écart-type de l'échantillon des sigmas (S_sigma_global)
    # ddof=1 pour avoir le (1 / N-1) de la formule
    std_dev_sample = np.std(data, ddof=1)

    # Degrés de liberté
    df = N - 1

    # Erreur standard (S / sqrt(N))
    standard_error = std_dev_sample / np.sqrt(N)

    # --- A. STATISTIQUE DE TEST T ---
    # Formule : (Moyenne - Seuil) / (S / sqrt(N))
    t_statistic = (mean_global - SEUIL_TOLERABLE_MICRONS) / standard_error

    # Valeur critique (t_alpha à N-1 ddl)
    # ppf(0.05) nous donne la valeur négative pour le test à gauche
    t_critical = stats.t.ppf(ALPHA, df)

    # --- B. INTERVALLE DE CONFIANCE (Borne Supérieure) ---
    # Formule : Moyenne + t(0.95, N-1) * (S / sqrt(N))
    # Note : t(0.95) est la valeur positive symétrique de t(0.05)
    t_conf_95 = stats.t.ppf(1 - ALPHA, df)
    ic_sup = mean_global + (t_conf_95 * standard_error)

    # 4. Rapport de Résultats
    print("\n" + "=" * 50)
    print(" RÉSULTATS DU TEST DE VALIDATION (Student t-test)")
    print("=" * 50)
    print(f" Hypothèse H0 : Sigma >= {SEUIL_TOLERABLE_MICRONS} µm")
    print(f" Hypothèse H1 : Sigma <  {SEUIL_TOLERABLE_MICRONS} µm (Cible)")
    print("-" * 50)
    print(f" Nombre d'échantillons (N)  : {N}")
    print(f" Moyenne globale (Sigma)    : {mean_global:.4f} µm")
    print(f" Écart-type échantillon (S) : {std_dev_sample:.4f} µm")
    print("-" * 50)

    print(" >> RÉSULTATS CALCULÉS :")
    print(f" Statistique t calculée     : {t_statistic:.4f}")
    print(f" Valeur critique (Alpha 5%) : {t_critical:.4f}")
    print(f" IC 95% Borne Supérieure    : {ic_sup:.4f} µm")
    print("-" * 50)

    # 5. Prise de Décision (Automatique)
    print(" >> CONCLUSION :")

    # Règle 1 : Test T
    if t_statistic < t_critical:
        res_t = "REJET de H0 -> SATISFAISANT"
        color_t = "✅"
    else:
        res_t = "NON-REJET de H0 -> INSUFFISANT"
        color_t = "❌"

    print(f" {color_t} Règle T-Student : {res_t}")
    print(f"    (Car {t_statistic:.4f} < {t_critical:.4f})")

    # Règle 2 : Intervalle de Confiance
    if ic_sup < SEUIL_TOLERABLE_MICRONS:
        res_ic = "SATISFAISANT"
        color_ic = "✅"
    else:
        res_ic = "INSUFFISANT"
        color_ic = "❌"

    print(f" {color_ic} Règle IC 95%    : {res_ic}")
    print(f"    (Car {ic_sup:.4f} µm < {SEUIL_TOLERABLE_MICRONS} µm)")
    print("=" * 50)


if __name__ == "__main__":
    # Installation auto de scipy si manquant : pip install scipy
    run_statistical_test()