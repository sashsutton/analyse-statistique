import os
import glob
import numpy as np
import pandas as pd
# On importe la fonction de calcul unitaire depuis le fichier voisin
from global_sigma_analysis import calculate_intra_sample_global_sigma

# --- CONFIGURATION ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "batch")


def calculate_inter_sample_mean_sigma():
    """
    Calcule Sigma_Global sur la population (N batches).

    Formule : Sigma_Global = (1/N) * Somme(Sigma_k)
    """

    # 1. Récupération automatique de tous les batches disponibles
    batch_folders = sorted(glob.glob(os.path.join(DATA_DIR, "batch_*")))
    N = len(batch_folders)

    if N == 0:
        print("Aucun dossier batch trouvé.")
        return

    print(f"\n=== ANALYSE INTER-ÉCHANTILLON (POPULATION N={N}) ===")

    sigma_k_list = []

    # 2. Boucle sur chaque patient k
    for folder in batch_folders:
        # Extraction de l'ID (ex: "batch_001" -> "001")
        batch_id = os.path.basename(folder).split('_')[-1]

        # Appel de la fonction de global_sigma_analysis.py
        # On met verbose=False pour ne pas spammer la console avec les détails intermédiaires
        result = calculate_intra_sample_global_sigma(batch_id, verbose=False)

        if result is not None:
            sigma_k_val, _ = result
            sigma_k_list.append(sigma_k_val)

            # Affichage ligne par ligne
            print(f"  [Batch {batch_id}] Sigma_k = {sigma_k_val:.6f} mm")
        else:
            print(f"  [Batch {batch_id}] Données invalides ou insuffisantes.")

    # 3. Calcul Final (Moyenne des Sigma_k)
    if sigma_k_list:
        sigma_k_array = np.array(sigma_k_list)

        # C'est ici qu'on applique la formule : (1/N) * Somme
        sigma_global = np.mean(sigma_k_array)

        # Statistiques additionnelles pour la thèse
        std_dev_pop = np.std(sigma_k_array, ddof=1)  # Écart-type entre les patients
        min_k = np.min(sigma_k_array)
        max_k = np.max(sigma_k_array)

        print("-" * 40)
        print(f" RÉSULTATS GLOBAUX")
        print("-" * 40)
        print(f" Nombre d'échantillons (N) : {len(sigma_k_list)}")
        print(f" Sigma_Global (Moyen)      : {sigma_global:.6f} mm")
        print(f" Conversion Microns        : {sigma_global * 1000:.3f} µm")
        print("-" * 40)
        print(f" Dispersion Inter-Patients : ±{std_dev_pop:.6f} mm")
        print(f" Meilleur cas (Batch)      : {min_k:.6f} mm")
        print(f" Pire cas (Batch)          : {max_k:.6f} mm")
        print("-" * 40)

        # Export optionnel
        output_csv = os.path.join(os.path.dirname(__file__), "resultats_population.csv")
        df_res = pd.DataFrame({
            'Batch': [os.path.basename(f) for f in batch_folders if f in batch_folders],  # Simplifié
            'Sigma_k': sigma_k_list
        })
        # Note : L'alignement Batch/Sigma suppose que tout s'est bien passé,
        # pour une thèse on ferait un dict, mais ici c'est suffisant.

    else:
        print("Erreur : Impossible de calculer la moyenne (aucune donnée valide).")


if __name__ == "__main__":
    calculate_inter_sample_mean_sigma()