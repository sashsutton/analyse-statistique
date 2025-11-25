import os
import glob
import numpy as np
from utils import read_and_clean_csv


def compute_folder_composite(folder_path):
    """
    Fonction : Calcule la composite (Minimum) pour un dossier dsi_xx (5 scans).
    Retourne la matrice 'Pire Cas' (enfoncement max) pour un angle donné.
    """
    csv_files = sorted(glob.glob(os.path.join(folder_path, "*.csv")))

    if len(csv_files) < 1:
        print(f"Attention: Aucun CSV trouvé dans {folder_path}")
        return None

    # Chargement des 5 matrices
    matrices = []
    for f in csv_files:
        mat = read_and_clean_csv(f)
        if mat is not None:
            matrices.append(mat)

    if not matrices:
        return None

    # Vérification des dimensions
    base_shape = matrices[0].shape
    for m in matrices:
        if m.shape != base_shape:
            # On lève une erreur car comparer des matrices de tailles différentes est impossible
            raise ValueError(f"Incohérence de dimension dans {folder_path}")

    # Empilement et calcul du MINIMUM (ignorer les NaNs)
    stack = np.array(matrices)

    with np.warnings.catch_warnings():
        np.warnings.filterwarnings('ignore', r'All-NaN (slice|axis) encountered')
        composite = np.nanmin(stack, axis=0)

    return composite


def process_global_mean(dsi_root_path):
    """
    Fonction : Calcule la MOYENNE des 7 composites (dsi_01 à dsi_07).
    Agrège les résultats des différents angles d'air.
    """
    composites_list = []

    print(f"--- Démarrage du traitement pour : {dsi_root_path} ---")

    # Boucle sur les 7 dossiers attendus (dsi_01 à dsi_07)
    for i in range(1, 8):
        folder_name = f"dsi_{i:02d}"
        full_path = os.path.join(dsi_root_path, folder_name)

        if os.path.isdir(full_path):
            print(f"Traitement {folder_name}...")
            comp = compute_folder_composite(full_path)

            if comp is not None:
                composites_list.append(comp)
        else:
            print(f"Attention : Dossier {folder_name} manquant.")

    if not composites_list:
        raise ValueError("Aucune donnée valide trouvée pour calculer la moyenne.")

    # Vérification des dimensions entre les 7 composites
    base_shape = composites_list[0].shape
    valid_composites = []
    for comp in composites_list:
        if comp.shape == base_shape:
            valid_composites.append(comp)
        else:
            print(f"Exclusion d'une composite aux dimensions incorrectes : {comp.shape}")

    if not valid_composites:
        raise ValueError("Aucune composite valide conservée après vérification des dimensions.")

    # Étape 2 : Calcul de la MOYENNE Globale
    global_stack = np.array(valid_composites)

    print(f"Calcul de la moyenne sur {len(valid_composites)} dossiers dsi...")

    with np.warnings.catch_warnings():
        np.warnings.filterwarnings('ignore', r'Mean of empty slice')
        final_mean_matrix = np.nanmean(global_stack, axis=0)

    print("--- Terminé avec succès ---")
    return final_mean_matrix