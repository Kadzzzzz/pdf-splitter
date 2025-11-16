# SPÉCIFICATIONS DÉTAILLÉES - COLLE SPLITTER

## CONTEXTE ET OBJECTIF

Je suis professeur et je donne des colles (interrogations orales) en physique et chimie. Je crée mes planches d'exercices en LaTeX qui génèrent un seul fichier PDF contenant toutes les planches. Je dois ensuite publier ces exercices individuellement sur mon site web, ce qui me prend actuellement beaucoup de temps car je dois :
1. Séparer manuellement les planches avec iLovePDF
2. Prendre des screenshots de chaque exercice
3. Renommer et organiser chaque fichier

**OBJECTIF** : Automatiser complètement ce processus avec un script Python simple et robuste.

---

## STRUCTURE DES FICHIERS PDF D'ENTRÉE

### Format type du PDF LaTeX

Le PDF d'entrée contient :

**Page 1 : Page de programme**
```
Colles de Chimie – Programme n°6
Semaines du 03 au 07 novembre
Jeremy Luccioni

Programme
— Atomistique : ...
— Tableau périodique : ...
— TP2 : Conductimétrie : ...
```

**Pages suivantes : Planches d'exercices**

Chaque planche commence par un titre de type :
```
Planche 1
```
ou
```
Planche 2
```
etc.

Chaque planche contient :
- **Questions de cours** (section optionnelle à ignorer pour l'extraction)
- **Un ou plusieurs exercices** identifiés par :
  - `Exercice : <titre>`
  - `Exercice n°X : <titre>`

### Exemple concret (voir fichier Colles-6.pdf fourni)

```
Page 1: Programme
Page 2: Planche 1 (contient 1 exercice : "Spectroscopie du diiode...")
Page 3: Planche 2 (contient 1 exercice : "Dosage du carbonate de lithium")
Page 4: Planche 3 (contient 1 exercice : "Dosage conductimétrique...")
```

---

## STRUCTURE DE SORTIE ATTENDUE

### Arborescence complète

```
public/
└── documents/
    └── exercices/
        ├── physique/
        │   ├── Colles-MPSI-S7/
        │   │   ├── Programme.pdf
        │   │   ├── P1-1.pdf
        │   │   ├── P1-2.pdf
        │   │   ├── P2.pdf      (un seul exercice)
        │   │   ├── P3-1.pdf
        │   │   └── P4-1.pdf    (planche bonus)
        │   └── Colles-MPSI-S8/
        │       └── ...
        └── chimie/
            ├── Colles-PCSI-S6/
            │   ├── Programme.pdf
            │   ├── P1.pdf
            │   ├── P2.pdf
            │   └── P3.pdf
            └── Colles-PCSI-S7/
                └── ...
```

### Convention de nommage

**Programme** : Toujours `Programme.pdf` (première page uniquement)

**Exercices** :
- Si **UN SEUL exercice** dans la planche : `P{numéro_planche}.pdf`
  - Exemple : `P1.pdf`, `P2.pdf`, `P3.pdf`
  
- Si **PLUSIEURS exercices** dans la planche : `P{numéro_planche}-{numéro_exercice}.pdf`
  - Exemple : `P1-1.pdf`, `P1-2.pdf`, `P2-1.pdf`, `P2-2.pdf`

**IMPORTANT** : La planche "bonus" (souvent Planche 4) suit la même logique avec P4, P4-1, P4-2, etc.

---

## ALGORITHME DE DÉTECTION

### Étape 1 : Extraction de la page Programme

- **Input** : PDF complet
- **Détection** : Première page (toujours page 1)
- **Output** : `Programme.pdf`

### Étape 2 : Détection des planches

**Pattern de détection** :
```
Regex : r"^Planche\s+(\d+)"
```

Pour chaque page :
1. Extraire le texte
2. Chercher le pattern "Planche X" en début de page
3. Si trouvé : Marquer le début d'une nouvelle planche
4. La planche s'étend jusqu'à la prochaine occurrence ou jusqu'à la fin du document

**Structure de données suggérée** :
```python
planches = {
    1: {"start_page": 2, "end_page": 2},
    2: {"start_page": 3, "end_page": 3},
    3: {"start_page": 4, "end_page": 4}
}
```

### Étape 3 : Détection des exercices dans chaque planche

**Patterns de détection** :
```python
patterns_exercices = [
    r"Exercice\s*:\s*(.+)",           # "Exercice : Titre"
    r"Exercice\s+n°(\d+)\s*:\s*(.+)", # "Exercice n°8 : Titre"
]
```

**Algorithme** :
1. Pour chaque planche, extraire le texte de toutes les pages de la planche
2. Compter le nombre d'occurrences des patterns d'exercices
3. Si 0 exercice détecté : **ERREUR** (lever une exception)
4. Si 1 exercice détecté : Créer `P{numéro}.pdf`
5. Si N exercices détectés (N > 1) : Créer `P{numéro}-1.pdf`, `P{numéro}-2.pdf`, ..., `P{numéro}-N.pdf`

**IMPORTANT** : Il faut découper la planche en N parties égales si plusieurs exercices.

**Calcul du découpage** :
```python
nombre_pages_planche = end_page - start_page + 1
pages_par_exercice = nombre_pages_planche / nombre_exercices

# Pour l'exercice i (1-indexed):
start = start_page + (i-1) * pages_par_exercice
end = start_page + i * pages_par_exercice - 1
```

---

## SPÉCIFICATIONS TECHNIQUES

### Technologies requises

- **Python 3.8+**
- **PyMuPDF (fitz)** : Manipulation PDF (extraction de pages, texte)
- **argparse** : Interface en ligne de commande
- **pathlib** : Gestion des chemins de fichiers
- **re** : Expressions régulières

### Interface en ligne de commande

```bash
python colle_splitter.py <fichier_pdf> --matiere <physique|chimie> --classe <MPSI|PCSI> --semaine <numero> [--output <chemin>]
```

**Arguments** :
- `fichier_pdf` (positionnel, obligatoire) : Chemin vers le PDF à découper
- `--matiere` ou `-m` (obligatoire) : `physique` ou `chimie`
- `--classe` ou `-c` (obligatoire) : `MPSI` ou `PCSI`
- `--semaine` ou `-s` (obligatoire) : Numéro de la semaine (ex: 6, 7, 8)
- `--output` ou `-o` (optionnel) : Dossier de sortie (défaut : `./public/documents/exercices/`)

**Exemples d'utilisation** :
```bash
# Exemple 1
python colle_splitter.py Colles-6.pdf -m chimie -c PCSI -s 6

# Exemple 2
python colle_splitter.py Colles-Physique-S7.pdf -m physique -c MPSI -s 7 -o /chemin/custom/

# Exemple 3 (format complet)
python colle_splitter.py ./input/Colles-6.pdf --matiere chimie --classe PCSI --semaine 6 --output ./output/
```

### Construction du chemin de sortie

```python
base_output = args.output  # défaut: ./public/documents/exercices/
matiere = args.matiere      # physique ou chimie
classe = args.classe        # MPSI ou PCSI
semaine = args.semaine      # 6, 7, etc.

dossier_final = base_output / matiere / f"Colles-{classe}-S{semaine}"
# Exemple: ./public/documents/exercices/chimie/Colles-PCSI-S6/
```

**Créer le dossier s'il n'existe pas** :
```python
dossier_final.mkdir(parents=True, exist_ok=True)
```

---

## STRUCTURE DU CODE

### Architecture suggérée

```
colle-splitter/
├── colle_splitter.py          # Script principal
├── requirements.txt           # Dépendances
├── README.md                  # Documentation
├── SPECIFICATIONS.md          # Ce fichier
├── tests/
│   ├── test_splitter.py       # Tests unitaires
│   └── sample_files/          # Fichiers PDF de test
└── .gitignore
```

### Modules et fonctions principales

```python
# colle_splitter.py

import fitz  # PyMuPDF
import argparse
import re
from pathlib import Path

def extraire_texte_page(pdf_doc, page_num):
    """Extrait le texte d'une page donnée"""
    pass

def detecter_planches(pdf_doc):
    """
    Détecte toutes les planches dans le PDF
    Returns: dict {numéro_planche: {"start_page": X, "end_page": Y}}
    """
    pass

def compter_exercices(pdf_doc, start_page, end_page):
    """
    Compte le nombre d'exercices dans une planche
    Returns: int (nombre d'exercices)
    """
    pass

def extraire_pages(pdf_doc, start_page, end_page, output_path):
    """
    Extrait un ensemble de pages et sauvegarde dans un nouveau PDF
    """
    pass

def extraire_programme(pdf_doc, output_dir):
    """
    Extrait la première page (Programme) et sauvegarde
    """
    pass

def traiter_planche(pdf_doc, num_planche, planche_info, output_dir):
    """
    Traite une planche complète :
    1. Compte les exercices
    2. Découpe selon le nombre
    3. Sauvegarde avec la bonne convention de nommage
    """
    pass

def main():
    """Point d'entrée principal"""
    # 1. Parser les arguments
    # 2. Ouvrir le PDF
    # 3. Créer le dossier de sortie
    # 4. Extraire Programme
    # 5. Détecter les planches
    # 6. Traiter chaque planche
    # 7. Afficher un récapitulatif
    pass

if __name__ == "__main__":
    main()
```

---

## GESTION DES ERREURS

### Erreurs à gérer

1. **Fichier PDF invalide ou introuvable**
   ```python
   if not Path(args.fichier_pdf).exists():
       raise FileNotFoundError(f"Le fichier {args.fichier_pdf} n'existe pas")
   ```

2. **Aucune planche détectée**
   ```python
   if not planches:
       raise ValueError("Aucune planche détectée dans le PDF")
   ```

3. **Aucun exercice détecté dans une planche**
   ```python
   if nb_exercices == 0:
       raise ValueError(f"Aucun exercice détecté dans la Planche {num}")
   ```

4. **Arguments invalides**
   ```python
   if args.matiere not in ['physique', 'chimie']:
       raise ValueError("--matiere doit être 'physique' ou 'chimie'")
   ```

### Messages utilisateur

Le script doit être **verbeux et informatif** :

```
🔍 Analyse du fichier : Colles-6.pdf
📄 Pages totales : 4

✅ Programme extrait : Programme.pdf

🔍 Détection des planches...
   ├─ Planche 1 détectée (page 2)
   ├─ Planche 2 détectée (page 3)
   └─ Planche 3 détectée (page 4)

📝 Traitement Planche 1 :
   └─ 1 exercice détecté → P1.pdf ✅

📝 Traitement Planche 2 :
   └─ 1 exercice détecté → P2.pdf ✅

📝 Traitement Planche 3 :
   └─ 1 exercice détecté → P3.pdf ✅

✨ Terminé ! 4 fichiers créés dans :
   → ./public/documents/exercices/chimie/Colles-PCSI-S6/
```

---

## CAS PARTICULIERS À GÉRER

### 1. Questions de cours

Les "Questions de cours" apparaissent souvent avant les exercices dans une planche.
- **NE PAS** les compter comme des exercices
- **NE PAS** créer de fichiers séparés pour elles
- Elles font partie du fichier de l'exercice suivant

### 2. Planches avec plusieurs exercices sur plusieurs pages

Exemple :
```
Planche 1 : pages 2-5 (4 pages)
- Exercice 1 : pages 2-3
- Exercice 2 : pages 4-5
```

Algorithme :
```python
# Si 2 exercices détectés sur 4 pages
pages_par_exercice = 4 / 2 = 2
# Exercice 1 : pages 2-3
# Exercice 2 : pages 4-5
```

### 3. Planche bonus (Planche 4)

Traiter exactement comme les autres planches : `P4.pdf`, `P4-1.pdf`, etc.

### 4. Numérotation non consécutive

Si les planches ne sont pas numérotées 1, 2, 3, 4 mais par exemple 1, 2, 4 :
- Conserver la numérotation originale
- Créer `P1.pdf`, `P2.pdf`, `P4.pdf` (pas de P3)

---

## TESTS ET VALIDATION

### Fichier de test

Utiliser le fichier `Colles-6.pdf` fourni comme test de référence.

**Résultat attendu** :
```
public/documents/exercices/chimie/Colles-PCSI-S6/
├── Programme.pdf (page 1)
├── P1.pdf (page 2)
├── P2.pdf (page 3)
└── P3.pdf (page 4)
```

### Tests unitaires suggérés

```python
# tests/test_splitter.py

def test_detection_planches():
    """Vérifie que 3 planches sont détectées dans Colles-6.pdf"""
    pass

def test_extraction_programme():
    """Vérifie que Programme.pdf contient exactement 1 page"""
    pass

def test_comptage_exercices():
    """Vérifie le nombre d'exercices par planche"""
    pass

def test_nommage_fichiers():
    """Vérifie que les fichiers sont nommés correctement"""
    pass
```

---

## EXIGENCES NON-FONCTIONNELLES

1. **Performance** : Traiter un PDF de 10 pages en < 5 secondes
2. **Robustesse** : Gérer les variations de mise en forme LaTeX
3. **Maintenabilité** : Code clair, commenté, modulaire
4. **Portabilité** : Compatible Windows, macOS, Linux
5. **Logs** : Messages clairs pour déboguer en cas de problème

---

## LIVRABLES ATTENDUS

1. ✅ `colle_splitter.py` - Script Python fonctionnel
2. ✅ `requirements.txt` - Dépendances
3. ✅ `README.md` - Documentation utilisateur
4. ✅ `.gitignore` - Fichiers à ignorer
5. ⚠️ `tests/` - Tests unitaires (optionnel mais recommandé)

---

## EXTENSIONS FUTURES (hors scope initial)

- Interface graphique (Tkinter ou web)
- Support de formats supplémentaires (images, Markdown)
- Détection automatique de la matière/classe depuis le PDF
- Upload automatique vers le site web
- Génération de métadonnées JSON pour chaque exercice

---

## CONTRAINTES ET NOTES IMPORTANTES

1. **Pas de modification du PDF source** : Le fichier original ne doit jamais être modifié
2. **Idempotence** : Relancer le script doit écraser les anciens fichiers sans erreur
3. **Encoding** : Gérer correctement les caractères spéciaux (accents français)
4. **Chemins relatifs** : Utiliser `pathlib` pour la compatibilité multi-OS
5. **Dépendances minimales** : Ne pas ajouter de bibliothèques inutiles

---

## EXEMPLE COMPLET D'EXÉCUTION

```bash
# Installation
pip install -r requirements.txt

# Exécution
python colle_splitter.py Colles-6.pdf -m chimie -c PCSI -s 6

# Résultat
🔍 Analyse du fichier : Colles-6.pdf
📄 Pages totales : 4

✅ Programme extrait : Programme.pdf

🔍 Détection des planches...
   ├─ Planche 1 détectée (page 2)
   ├─ Planche 2 détectée (page 3)
   └─ Planche 3 détectée (page 4)

📝 Traitement Planche 1 :
   └─ 1 exercice détecté → P1.pdf ✅

📝 Traitement Planche 2 :
   └─ 1 exercice détecté → P2.pdf ✅

📝 Traitement Planche 3 :
   └─ 1 exercice détecté → P3.pdf ✅

✨ Terminé ! 4 fichiers créés dans :
   → ./public/documents/exercices/chimie/Colles-PCSI-S6/

# Vérification
ls -la public/documents/exercices/chimie/Colles-PCSI-S6/
total 120
drwxr-xr-x  6 user  staff   192 Nov 16 10:30 .
drwxr-xr-x  3 user  staff    96 Nov 16 10:30 ..
-rw-r--r--  1 user  staff  8234 Nov 16 10:30 Programme.pdf
-rw-r--r--  1 user  staff 15678 Nov 16 10:30 P1.pdf
-rw-r--r--  1 user  staff 12456 Nov 16 10:30 P2.pdf
-rw-r--r--  1 user  staff 14523 Nov 16 10:30 P3.pdf
```

---

## RESSOURCES

- Documentation PyMuPDF : https://pymupdf.readthedocs.io/
- Expressions régulières Python : https://docs.python.org/3/library/re.html
- argparse : https://docs.python.org/3/library/argparse.html

---

**FIN DES SPÉCIFICATIONS**

Date : 16 novembre 2025
Auteur : Jeremy Luccioni
Version : 1.0
