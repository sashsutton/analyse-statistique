import os
import glob
import numpy as np
import pandas as pd
import warnings

# --- CONFIGURATION ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "batch")
NOISE_VALUE = -999.99
TOLERANCE = 1e-5


def read_and_clean_csv(filepath):
    """Lit un CSV et gère les NaN."""
    try:
        df = pd.read_csv(filepath, header=None, dtype=np.float32)
        matrix = df.values
        matrix[matrix <= (NOISE_VALUE + TOLERANCE)] = np.nan
        return matrix
    except Exception as e:
        return None


def calculate_intra_sample_global_sigma(batch_id, verbose=True):
    """
    Calcule Sigma_k (Écart-type moyen) pour UN batch spécifique.
    Retourne (valeur_sigma_k, map_sigma_jk).
    """
    batch_folder = f"batch_{batch_id}"
    dsi_root = os.path.join(DATA_DIR, batch_folder, "dsi")

    if not os.path.exists(dsi_root):
        if verbose: print(f"[Erreur] Dossier introuvable : {dsi_root}")
        return None

    if verbose: print(f"--- Traitement Intra-Sample : {batch_folder} ---")

    # 1. Chargement des matrices
    matrices_list = []
    for i in range(1, 8):
        subfolder = f"dsi_{i:02d}"
        search_path = os.path.join(dsi_root, subfolder, "min_composite_*.csv")
        found = glob.glob(search_path)

        if found:
            mat = read_and_clean_csv(found[0])
            if mat is not None:
                matrices_list.append(mat)

    if len(matrices_list) < 2:
        if verbose: print(f"  [Skip] Pas assez de données dans {batch_folder}")
        return None

    # 2. Calcul Vectorisé
    stack = np.array(matrices_list)

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', r'Degrees of freedom <= 0')
        # Sigma_jk pour chaque pixel
        sigma_map_jk = np.nanstd(stack, axis=0, ddof=1)

    # 3. Moyenne Globale Sigma_k
    # On fait la moyenne de tous les écarts-types locaux
    sigma_k = np.nanmean(sigma_map_jk)

    return sigma_k, sigma_map_jk


if __name__ == "__main__":
    # Test unitaire
    TARGET = "001"
    res = calculate_intra_sample_global_sigma(TARGET, verbose=True)
    if res:
        print(f"Résultat Sigma_k pour {TARGET} : {res[0]:.6f} mm")