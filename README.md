# README - Analyse de la Compressibilité Gingivale (3D)

## Contexte du Projet

Ce projet s'inscrit dans le cadre d'une thèse en dentaire visant à quantifier la compressibilité des tissus mous (gencive) **in vivo**. L'objectif est de mesurer la déformation de la gencive sous l'effet d'une pression d'air calibrée, en utilisant un scanner intra-oral.

### Méthode d'acquisition

Le scanner utilise une technologie de **profilométrie laser** : il projette des lignes et enregistre une *Height Map* (carte de hauteurs) où chaque pixel correspond à une altitude ( Z ).

* **Scan A (Baseline)** : mâchoire au repos (sans pression).
* **Scan B (Sous contrainte)** : projection d'un jet d'air comprimé pour enfoncer les tissus mous au point d'impact.

---

## Structure des Données (Input)

Les données sont organisées de manière hiérarchique : lot → patient → type de mesure.

### Arborescence

```
batch_i/
├── dpi/                  [RÉFÉRENCE - REPOS]
│   └── dpi_height.csv    (Scan unique de la mâchoire sans air)
│
└── dsi/                  [EXPÉRIMENTATION - PRESSION]
    ├── dsi_01/           (Angle d'air n°1)
    │   ├── scan_1.csv    (Répétition 1)
    │   ├── ...
    │   └── scan_5.csv    (Répétition 5)
    ├── dsi_02/           (Angle d'air n°2)
    ├── ...
    └── dsi_07/           (Angle d'air n°7)
```

### Spécifications des fichiers CSV

* **Format** : CSV sans en-tête.
* **Type** : matrice 2D de flottants (Height Map).
* **Unités** :

  * Axes X/Y : 1 pixel = 12.5 µm (0.0125 mm)
  * Axe Z : hauteur en mm
* **Valeur sentinelle** : les zones non mesurées ou bruitées sont marquées **-999.99**.

---

## Pré-requis

* Python 3.8+
* Bibliothèques : `numpy`, `pandas`, `scipy`

---

