import os
import glob
import numpy as np
import pandas as pd
import warnings

# --- CONFIGURATION ---
ROOT_DIR = "./batch"  # Dossier racine
NOISE_VALUE = -999.9999  # La valeur exacte à écrire dans le CSV final
TOLERANCE = 1e-5


def read_and_clean_csv(filepath):
    """
    Lit un CSV et remplace le bruit (-999.9999) par NaN
    pour permettre les calculs mathématiques corrects.
    """
    try:
        df = pd.read_csv(filepath, header=None, dtype=np.float32)
        matrix = df.values
        # On convertit en NaN pour les calculs (sinon min() prendrait -999)
        matrix[matrix <= (NOISE_VALUE + TOLERANCE)] = np.nan
        return matrix
    except Exception as e:
        print(f"    [Erreur] Lecture impossible de {os.path.basename(filepath)}")
        return None


def save_matrix_with_noise(matrix, filepath):
    """
    Fonction utilitaire pour sauvegarder :
    Remplace les NaN par NOISE_VALUE (-999.9999) avant d'écrire le CSV.
    """
    # On remplit les trous (NaN) avec la valeur de bruit
    df_to_save = pd.DataFrame(matrix).fillna(NOISE_VALUE)

    # On sauvegarde avec 4 décimales pour respecter le format d'origine
    df_to_save.to_csv(filepath, header=False, index=False, float_format="%.4f")


def compute_and_save_angle_composite(folder_path, repetition_name):
    """
    1. Lit les 5 angles.
    2. Calcule le MINIMUM (en ignorant les NaN).
    3. Restaure les -999.9999 et sauvegarde.
    """
    # Récupération des 5 fichiers
    csv_files = sorted(glob.glob(os.path.join(folder_path, "scan_*.csv")))

    # Fallback si les noms ne sont pas "scan_x.csv"
    if not csv_files:
        all_files = sorted(glob.glob(os.path.join(folder_path, "*.csv")))
        csv_files = [f for f in all_files if "min_composite" not in os.path.basename(f)]

    valid_matrices = []
    for f in csv_files:
        mat = read_and_clean_csv(f)
        if mat is not None:
            valid_matrices.append(mat)

    if not valid_matrices:
        return None

    # Empilement
    stack = np.array(valid_matrices)

    # Calcul du MINIMUM (Intra-Calcul : on garde les NaN)
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', r'All-NaN (slice|axis) encountered')
        composite_min = np.nanmin(stack, axis=0)

    # --- SAUVEGARDE (Conversion NaN -> -999.9999) ---
    output_filename = f"min_composite_{repetition_name}.csv"
    output_path = os.path.join(folder_path, output_filename)

    try:
        save_matrix_with_noise(composite_min, output_path)
        # print(f"    -> Sauvegardé : {repetition_name}/{output_filename}")
    except Exception as e:
        print(f"    -> Erreur sauvegarde {repetition_name}: {e}")

    return composite_min


def process_batch(batch_path, batch_name):
    """
    Traite un patient complet.
    """
    dsi_root = os.path.join(batch_path, "dsi")

    if not os.path.exists(dsi_root):
        print(f"  [Attention] 'dsi' introuvable dans {batch_name}")
        return

    repetitions_list = []

    # Boucle sur les 7 répétitions statistiques
    for i in range(1, 8):
        subfolder_name = f"dsi_{i:02d}"
        subfolder_path = os.path.join(dsi_root, subfolder_name)

        if os.path.isdir(subfolder_path):
            # Calcul du composite
            comp = compute_and_save_angle_composite(subfolder_path, subfolder_name)
            if comp is not None:
                repetitions_list.append(comp)

    if not repetitions_list:
        print(f"  [Erreur] Aucune donnée valide pour {batch_name}")
        return

    # Calcul de la MOYENNE GLOBALE des 7 répétitions
    # (Toujours avec NaN pour la précision mathématique)
    stack_repetitions = np.array(repetitions_list)
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', r'Mean of empty slice')
        final_mean_composite = np.nanmean(stack_repetitions, axis=0)

    # --- SAUVEGARDE FINALE (Conversion NaN -> -999.9999) ---
    try:
        batch_id = batch_name.split('_')[-1]
    except:
        batch_id = "unknown"

    filename = f"dsi_mean_{batch_id}.csv"
    save_path = os.path.join(dsi_root, filename)

    try:
        save_matrix_with_noise(final_mean_composite, save_path)
        print(f"  -> {filename} créé (Bruit restauré).")
    except Exception as e:
        print(f"  -> Erreur écriture finale : {e}")


def main():
    batch_folders = sorted(glob.glob(os.path.join(ROOT_DIR, "batch_*")))
    print(f"Traitement des données brutes ({len(batch_folders)} patients)...")

    for batch_path in batch_folders:
        batch_name = os.path.basename(batch_path)
        # print(f"--- Traitement {batch_name} ---")
        process_batch(batch_path, batch_name)

    print("\n=== TRAITEMENT TERMINÉ ===")
    print("Les fichiers dsi_mean et min_composite contiennent maintenant -999.9999 pour les zones vides.")


if __name__ == "__main__":
    main()