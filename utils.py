import numpy as np
import pandas as pd

# --- CONSTANTES ---
NOISE_VALUE = -999.99
TOLERANCE = 1e-5  # Pour la comparaison des floats


def read_and_clean_csv(filepath):
    """
    Lit un fichier CSV et remplace les valeurs de bruit par NaN.
    """
    try:
        # Lecture optimisée : header=None car pas d'en-tête, dtype float32 pour la mémoire
        df = pd.read_csv(filepath, header=None, dtype=np.float32)
        matrix = df.values

        # Masquage du bruit (-999.99)
        # On utilise une condition <= pour attraper -999.99 et potentiellement moins
        matrix[matrix <= (NOISE_VALUE + TOLERANCE)] = np.nan
        return matrix
    except Exception as e:
        print(f"Erreur de lecture sur {filepath}: {e}")
        return None