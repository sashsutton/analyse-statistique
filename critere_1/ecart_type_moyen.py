import numpy as np


from ecart_type_point import calculate_point_sigma

def calculate_patient_global_sigma_iterative(matrices_list):
    """
    Calcule Sigma_k en bouclant explicitement sur chaque point (i, j).
    C'est la traduction littérale de la somme mathématique.
    """

    # 1. On récupère les dimensions (7 scans, Hauteur H, Largeur W)
    # On convertit en array juste pour lire les dimensions
    stack = np.array(matrices_list)
    nb_scans, height, width = stack.shape

    sigma_values = []  # Liste pour stocker tous les sigma_jk valides

    print(f"Début du calcul itératif sur {height}x{width} points...")

    # 2. DOUBLE BOUCLE : On parcourt toute la matrice point par point
    for i in range(height):
        for j in range(width):

            # --- C'EST ICI QU'ON UTILISE VOTRE FONCTION PRÉCÉDENTE ---
            # On calcule le sigma local pour ce point précis
            sigma_jk = calculate_point_sigma(matrices_list, i, j)

            # Si le calcul est valide (pas NaN), on l'ajoute à la liste globale
            if not np.isnan(sigma_jk):
                sigma_values.append(sigma_jk)

    # 3. Calcul de la MOYENNE GLOBALE
    # P_k correspond ici à len(sigma_values) (nombre de points valides)
    if len(sigma_values) == 0:
        return np.nan

    sigma_k = np.mean(sigma_values)

    return sigma_k