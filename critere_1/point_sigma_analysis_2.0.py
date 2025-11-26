import os
import glob
import numpy as np
import pandas as pd

# --- CONFIGURATION ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "batch")


def get_pixel_value_safe(filepath, row, col):
    """Lit la valeur d'un pixel (i,j) dans un CSV."""
    try:
        # On lit le CSV sans header
        df = pd.read_csv(filepath, header=None, dtype=np.float32)

        # Vérification des bornes
        if row >= df.shape[0] or col >= df.shape[1]:
            return np.nan

        val = df.iloc[row, col]
        return val if val > -999.0 else np.nan
    except:
        return np.nan


def calculate_point_sigma_vectorized(batch_id, row_i, col_j):
    """
    Version 2.0 : Calcul vectorisé (Numpy) de l'écart-type pour un point (i, j).
    """
    batch_folder = f"batch_{batch_id}"
    dsi_root = os.path.join(DATA_DIR, batch_folder, "dsi")

    if not os.path.exists(dsi_root):
        print(f"Erreur : {dsi_root} introuvable.")
        return

    print(f"\n--- ANALYSE VECTORISÉE (2.0) DU POINT ({row_i}, {col_j}) ---")
    print(f"Patient : {batch_folder}")

    # 1. Extraction des données (Création du vecteur)
    # On parcourt les 7 répétitions pour construire un vecteur numpy de taille 7
    z_values = []

    for k in range(1, 8):
        subfolder = f"dsi_{k:02d}"
        pattern = os.path.join(dsi_root, subfolder, "min_composite_*.csv")
        files = glob.glob(pattern)

        val = np.nan
        if files:
            val = get_pixel_value_safe(files[0], row_i, col_j)

        z_values.append(val)
        # Affichage compact
        print(f"  Scan {k} : {val:.4f}" if not np.isnan(val) else f"  Scan {k} : NaN")

    # 2. Vectorisation (Le cœur de la V2.0)
    # On transforme la liste en Array Numpy
    z_vector = np.array(z_values, dtype=np.float32)

    # Vérification du nombre de points valides (P_jk)
    valid_count = np.sum(~np.isnan(z_vector))

    if valid_count < 2:
        print("\n[!] Calcul impossible : Pas assez de données valides.")
        return

    # 3. Calcul de Sigma
    # np.nanstd fait tout le travail mathématique (Moyenne, Diff au carré, Somme, Racine)
    # ddof=1 active la correction de Bessel (division par N-1)
    sigma_jk = np.nanstd(z_vector, ddof=1)

    z_mean = np.nanmean(z_vector)

    # --- RÉSULTATS ---
    print("-" * 30)
    print(f"Moyenne Locale (Z_jk) : {z_mean:.5f} mm")
    print(f"ÉCART-TYPE (Sigma_jk) : {sigma_jk:.5f} mm")
    print(f"Variation (microns)   : {sigma_jk * 1000:.2f} µm")
    print("-" * 30)


if __name__ == "__main__":
    # Paramètres de test
    BATCH = "001"
    ROW = 500
    COL = 500

    calculate_point_sigma_vectorized(BATCH, ROW, COL)