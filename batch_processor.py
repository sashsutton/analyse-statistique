import os
import glob
import numpy as np
import pandas as pd
import warnings

# --- CONFIGURATION ---
ROOT_DIR = "./batch"  # Dossier racine
NOISE_VALUE = -999.99
TOLERANCE = 1e-5


def read_and_clean_csv(filepath):
    """Lit un CSV et remplace -999.99 par NaN."""
    try:
        df = pd.read_csv(filepath, header=None, dtype=np.float32)
        matrix = df.values
        matrix[matrix <= (NOISE_VALUE + TOLERANCE)] = np.nan
        return matrix
    except Exception as e:
        print(f"    [Erreur] Lecture impossible de {os.path.basename(filepath)}")
        return None


def compute_and_save_angle_composite(folder_path, repetition_name):
    """
    Traite une répétition statistique (un dossier dsi_xx).

    CONTEXTE : Ce dossier contient 5 scans pris sous 5 ANGLES D'INCIDENCE différents.
    LOGIQUE  : On calcule le MINIMUM des 5 angles.
               Cela permet de capturer la profondeur maximale (Z min) atteinte par l'air,
               indépendamment de l'angle de prise de vue.

    SORTIE   : Sauvegarde immédiate de 'min_composite_dsi_xx.csv'.
    """
    # Récupération des 5 fichiers correspondant aux 5 angles
    csv_files = sorted(glob.glob(os.path.join(folder_path, "scan_*.csv")))

    # Fallback si les noms ne sont pas "scan_x.csv"
    if not csv_files:
        all_files = sorted(glob.glob(os.path.join(folder_path, "*.csv")))
        # On exclut les fichiers résultats (min_composite) pour ne pas lire nos propres outputs
        csv_files = [f for f in all_files if "min_composite" not in os.path.basename(f)]

    valid_matrices = []
    for f in csv_files:
        mat = read_and_clean_csv(f)
        if mat is not None:
            valid_matrices.append(mat)

    if not valid_matrices:
        return None

    # Empilement des 5 angles
    stack = np.array(valid_matrices)

    # Calcul du MINIMUM (Pour obtenir l'empreinte maximale parmi les 5 angles)
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', r'All-NaN (slice|axis) encountered')
        composite_min = np.nanmin(stack, axis=0)

    # --- SAUVEGARDE INTERMÉDIAIRE ---
    output_filename = f"min_composite_{repetition_name}.csv"
    output_path = os.path.join(folder_path, output_filename)

    try:
        pd.DataFrame(composite_min).to_csv(output_path, header=False, index=False)
        print(f"    -> Sauvegardé (Composite des angles) : {repetition_name}/{output_filename}")
    except Exception as e:
        print(f"    -> Erreur sauvegarde {repetition_name}: {e}")

    return composite_min


def process_batch(batch_path, batch_name):
    """
    Traite un patient complet (Batch).

    CONTEXTE : On dispose de 7 dossiers (dsi_01 à dsi_07) qui sont 7 RÉPÉTITIONS
               de l'expérience dans les mêmes conditions.
    LOGIQUE  : On fait la MOYENNE des 7 résultats pour la robustesse statistique.
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
            # Calcul du composite (Min des angles) pour cette répétition
            comp = compute_and_save_angle_composite(subfolder_path, subfolder_name)
            if comp is not None:
                repetitions_list.append(comp)

    if not repetitions_list:
        print(f"  [Erreur] Aucune donnée valide pour {batch_name}")
        return

    # Calcul de la MOYENNE GLOBALE des 7 répétitions
    stack_repetitions = np.array(repetitions_list)
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', r'Mean of empty slice')
        final_mean_composite = np.nanmean(stack_repetitions, axis=0)

    # Sauvegarde Globale (dsi_mean_XXX.csv)
    try:
        batch_id = batch_name.split('_')[-1]
    except:
        batch_id = "unknown"

    filename = f"dsi_mean_{batch_id}.csv"
    save_path = os.path.join(dsi_root, filename)

    try:
        pd.DataFrame(final_mean_composite).to_csv(save_path, header=False, index=False)
        print(f"  -> SUCCESS FINAL (Moyenne Statistique) : {filename} créé dans {dsi_root}")
    except Exception as e:
        print(f"  -> Erreur écriture finale : {e}")


def main():
    batch_folders = sorted(glob.glob(os.path.join(ROOT_DIR, "batch_*")))
    print(f"Démarrage : {len(batch_folders)} lots détectés.\n")

    for batch_path in batch_folders:
        batch_name = os.path.basename(batch_path)
        print(f"--- Traitement de {batch_name} ---")
        process_batch(batch_path, batch_name)
        print("")

    print("=== TRAITEMENT TERMINÉ ===")


if __name__ == "__main__":
    main()