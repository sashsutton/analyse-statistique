import numpy as np


def calculate_point_sigma(matrices_list, row_idx, col_idx):
    """
    Calcule l'écart-type (Sample Standard Deviation) pour un point précis (i, j)
    à travers M scans.

    Args:
        matrices_list (list): Liste des 7 matrices (scans composites).
        row_idx (int): L'index de la ligne (i).
        col_idx (int): L'index de la colonne (j).

    Returns:
        float: L'écart-type (sigma) à ce point. Retourne NaN si calcul impossible.
    """

    # 1. Extraction du vecteur Z : On récupère la valeur (i, j) dans chaque matrice
    # Cela crée une liste de M valeurs : [z1, z2, ..., z7]
    z_values = [mat[row_idx, col_idx] for mat in matrices_list]

    # Conversion en array numpy pour faciliter le traitement
    z_array = np.array(z_values)

    # 2. Nettoyage : On ne garde que les valeurs qui ne sont pas NaN
    # (Si un scan avait du bruit à cet endroit, on l'exclut du calcul)
    valid_z = z_array[~np.isnan(z_array)]

    M_valid = len(valid_z)

    # Sécurité : Il faut au moins 2 valeurs pour calculer un écart-type
    if M_valid < 2:
        return np.nan

    # 3. Application de la formule mathématique
    # Formule : sqrt( (1/(M-1)) * sum( (Z - Mean)^2 ) )

    # Calcul manuel pour la transparence (identique à np.std(..., ddof=1))
    mean_z = np.mean(valid_z)  # Moyenne Zjk
    squared_diffs = (valid_z - mean_z) ** 2  # (Zijk - Zjk)^2
    sum_sq_diffs = np.sum(squared_diffs)  # Somme
    variance = sum_sq_diffs / (M_valid - 1)  # Division par M-1
    sigma = np.sqrt(variance)  # Racine carrée

    return sigma