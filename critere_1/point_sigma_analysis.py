import os
import sys
import glob
import numpy as np
import pandas as pd

# --- CONFIGURATION ---
# Chemin relatif pour remonter d'un cran (..) puis aller dans batch
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "batch")


def get_pixel_value_from_csv(filepath, row_idx, col_idx):
    """
    Lit un fichier CSV et extrait la valeur à (row, col).
    Retourne float ou np.nan
    """
    try:
        # On lit le CSV (header=None).
        # Note : Pour l'optimisation, si les fichiers sont énormes,
        # lire tout le fichier pour un point est lent, mais c'est le plus simple ici.
        df = pd.read_csv(filepath, header=None, dtype=np.float32)

        # Vérification des bornes
        if row_idx >= df.shape[0] or col_idx >= df.shape[1]:
            print(f"  [Erreur] Point ({row_idx}, {col_idx}) hors limites pour {os.path.basename(filepath)}")
            return np.nan

        value = df.iloc[row_idx, col_idx]

        # Gestion du bruit (-999.99)
        if value <= -999.0:
            return np.nan

        return value
    except Exception as e:
        print(f"  [Erreur Fichier] {e}")
        return np.nan


def calculate_point_sigma(batch_id, row_i, col_j):
    """
    Calcule l'écart-type (Sigma) pour le point (i, j) sur les 7 répétitions du batch_k.
    """
    batch_folder = f"batch_{batch_id}"  # ex: batch_001
    dsi_root = os.path.join(DATA_DIR, batch_folder, "dsi")

    if not os.path.exists(dsi_root):
        print(f"Erreur : Dossier introuvable -> {dsi_root}")
        return

    print(f"\n--- ANALYSE DU POINT ({row_i}, {col_j}) pour {batch_folder} ---")

    values_z_ijk = []  # Liste pour stocker les 7 valeurs z_ijk

    # On boucle sur les 7 dossiers de répétition (dsi_01 à dsi_07)
    for x in range(1, 8):
        subfolder = f"dsi_{x:02d}"

        # On cherche le fichier 'min_composite_*.csv' créé par l'étape précédente
        search_pattern = os.path.join(dsi_root, subfolder, "min_composite_*.csv")
        found_files = glob.glob(search_pattern)

        if found_files:
            file_path = found_files[0]  # On prend le fichier composite trouvé

            # Extraction de la valeur du point
            val = get_pixel_value_from_csv(file_path, row_i, col_j)

            # Affichage pour contrôle
            display_val = f"{val:.4f}" if not np.isnan(val) else "NaN (Bruit)"
            print(f"  Repétition {x} ({subfolder}) : Z = {display_val}")

            values_z_ijk.append(val)
        else:
            print(f"  Repétition {x} : Fichier min_composite introuvable.")
            values_z_ijk.append(np.nan)

    # --- CALCUL MATHÉMATIQUE ---

    # Conversion en numpy array pour le calcul
    data = np.array(values_z_ijk)

    # On filtre les NaN (si une répétition a échoué sur ce point)
    valid_data = data[~np.isnan(data)]
    M = len(valid_data)  # Nombre de valeurs valides

    if M < 2:
        print("\n[RÉSULTAT] Calcul impossible (moins de 2 valeurs valides).")
        return

    # 1. Calcul de la moyenne z_jk (sur ce point spécifique)
    z_jk_mean = np.mean(valid_data)

    # 2. Calcul de la somme des carrés des écarts : Somme((z_ijk - z_jk)^2)
    sum_squared_diffs = np.sum((valid_data - z_jk_mean) ** 2)

    # 3. Division par M-1 (Correction de Bessel pour l'échantillon)
    variance = sum_squared_diffs / (M - 1)

    # 4. Racine carrée pour obtenir l'écart-type
    sigma_jk = np.sqrt(variance)

    # --- RÉSULTATS ---
    print("-" * 40)
    print(f"Nombre de mesures valides (M) : {M} / 7")
    print(f"Moyenne locale (z_jk)       : {z_jk_mean:.5f} mm")
    print(f"Écart-Type (sigma_jk)       : {sigma_jk:.5f} mm")

    # Interprétation rapide
    microns = sigma_jk * 1000
    print(f"Variation estimée           : {microns:.2f} µm")
    print("-" * 40)


if __name__ == "__main__":
    # --- PARAMÈTRES À MODIFIER POUR TESTER ---
    TARGET_BATCH = "001"  # Le 'k' (numéro du batch)
    TARGET_I = 500  # Coordonnée Ligne (Row)
    TARGET_J = 500  # Coordonnée Colonne (Col)

    calculate_point_sigma(TARGET_BATCH, TARGET_I, TARGET_J)