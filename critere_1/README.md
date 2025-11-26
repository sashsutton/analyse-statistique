# Critère 1 : Analyse de la Variabilité de la Mesure

Ce module contient les scripts statistiques pour valider la reproductibilité du protocole DSI.

## 📊 1. Indicateurs Mathématiques

L'analyse suit une hiérarchie stricte :

* **Niveau 1 (Local) :** $\sigma_{jk}$ (Écart-type par pixel sur 7 répétitions).
* **Niveau 2 (Patient) :** $\Sigma_k$ (Moyenne des écarts-types locaux).
* **Niveau 3 (Global) :** $\bar{\sigma}_{global}$ (Moyenne des $\Sigma_k$ sur $N$ patients).

---

## 🧪 2. Validation Statistique (Test de Student)

Le fichier `statistical_validation.py` implémente les tests d'hypothèses définis dans le protocole de thèse.

### 2.1 Hypothèses
On cherche à démontrer que la reproductibilité moyenne est strictement inférieure au seuil clinique de **20 µm**.

* **H0** : $\bar{\sigma}_{global} \ge 20 \mu m$
* **H1** : $\bar{\sigma}_{global} < 20 \mu m$ (Test unilatéral gauche, $\alpha = 0.05$)

### 2.2 Statistique de Test
On utilise un test t à un échantillon basé sur la loi de Student à $N-1$ degrés de liberté.

$$t = \frac{\bar{\sigma}_{global} - 20}{\sigma_{\sigma_{global}} / \sqrt{N}}$$

Où :
* $\bar{\sigma}_{global}$ est la moyenne de l'échantillon.
* $\sigma_{\sigma_{global}}$ est l'écart-type de l'échantillon des valeurs $\Sigma_k$.

### 2.3 Règles de Décision (Implémentées)

Le script vérifie automatiquement les deux conditions de succès :

1.  **Test T :** Si $t_{calculé} < t_{\alpha, N-1}$ (valeur critique négative), alors on rejette $H_0$. La reproductibilité est jugée **SATISFAISANTE**.
2.  **Intervalle de Confiance :** Si la borne supérieure de l'IC à 95% est inférieure à 20 µm, la reproductibilité est **SATISFAISANTE**.

**Formule de l'IC Supérieur (basée sur votre note manuscrite) :**

$$IC_{95\%, sup} = \bar{\sigma}_{global} + t_{0.95; N-1} \times \frac{\sigma_{\sigma_{global}}}{\sqrt{N}}$$

---

## 📂 Scripts Python

| Script | Fonction |
| :--- | :--- |
| `point_sigma_analysis_2.0.py` | Micro-analyse vectorisée d'un point $(i,j)$. |
| `global_sigma_analysis.py` | Calcul du $\Sigma_k$ pour un patient. |
| `population_sigma_analysis.py` | Calcul de la moyenne brute de la population. |
| **`statistical_validation.py`** | **Script Final.** Exécute le test statistique et donne le verdict (Satisfaisant/Insuffisant). |

## 🚀 Utilisation

Pour obtenir la validation finale de votre thèse :

```bash
cd critere_1
python statistical_validation.py