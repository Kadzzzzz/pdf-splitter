# PROMPT POUR CLAUDE CODE

## MISSION

Tu es un développeur Python expert. Je veux que tu crées un script Python complet et fonctionnel pour automatiser l'extraction et l'organisation d'exercices de colles à partir de fichiers PDF LaTeX.

**Lis ABSOLUMENT le fichier `SPECIFICATIONS.md` en premier** - il contient TOUTES les informations nécessaires.

## INSTRUCTIONS ÉTAPE PAR ÉTAPE

### 1. LIRE LA DOCUMENTATION

**AVANT TOUT** :
```bash
# Lis ces fichiers dans l'ordre :
1. SPECIFICATIONS.md  (LE PLUS IMPORTANT - toutes les specs détaillées)
2. STRUCTURE_EXAMPLE.md (exemples de sortie)
3. README.md (contexte général)
```

### 2. CRÉER LE SCRIPT PRINCIPAL

Crée `colle_splitter.py` avec cette structure EXACTE :

```python
#!/usr/bin/env python3
"""
Colle Splitter - Outil d'extraction automatique d'exercices depuis des planches PDF
Auteur: Jeremy Luccioni
Date: Novembre 2025
"""

import fitz  # PyMuPDF
import argparse
import re
from pathlib import Path
import sys


def extraire_texte_page(pdf_doc, page_num):
    """
    Extrait le texte d'une page donnée du PDF.
    
    Args:
        pdf_doc: Document PyMuPDF
        page_num: Numéro de page (0-indexed)
    
    Returns:
        str: Texte de la page
    """
    # TODO: Implémenter
    pass


def detecter_planches(pdf_doc):
    """
    Détecte toutes les planches dans le PDF en cherchant le pattern "Planche X".
    
    Pattern utilisé: r"^Planche\s+(\d+)" au début d'une ligne
    
    Args:
        pdf_doc: Document PyMuPDF
    
    Returns:
        dict: {numéro_planche: {"start_page": X, "end_page": Y}}
              où X et Y sont en 0-indexed
    
    Exemple:
        {
            1: {"start_page": 1, "end_page": 1},
            2: {"start_page": 2, "end_page": 2},
            3: {"start_page": 3, "end_page": 3}
        }
    """
    # TODO: Implémenter
    # IMPORTANT: La page 0 est le Programme, les planches commencent à la page 1
    pass


def compter_exercices(pdf_doc, start_page, end_page):
    """
    Compte le nombre d'exercices dans une planche donnée.
    
    Patterns recherchés (dans l'ordre) :
    - r"Exercice\s*:\s*(.+)"           → "Exercice : Titre"
    - r"Exercice\s+n°(\d+)\s*:\s*(.+)" → "Exercice n°8 : Titre"
    
    IMPORTANT: NE PAS compter "Questions de cours" comme un exercice
    
    Args:
        pdf_doc: Document PyMuPDF
        start_page: Page de début (0-indexed)
        end_page: Page de fin (0-indexed, inclusive)
    
    Returns:
        int: Nombre d'exercices détectés
    
    Raises:
        ValueError: Si 0 exercice détecté
    """
    # TODO: Implémenter
    pass


def extraire_pages(pdf_doc, start_page, end_page, output_path):
    """
    Extrait un ensemble de pages du PDF et sauvegarde dans un nouveau fichier.
    
    Args:
        pdf_doc: Document PyMuPDF source
        start_page: Page de début (0-indexed)
        end_page: Page de fin (0-indexed, inclusive)
        output_path: Chemin du fichier de sortie (Path object)
    """
    # TODO: Implémenter avec pdf_doc.select()
    pass


def extraire_programme(pdf_doc, output_dir):
    """
    Extrait la première page (Programme) et la sauvegarde.
    
    Args:
        pdf_doc: Document PyMuPDF
        output_dir: Dossier de sortie (Path object)
    
    Returns:
        Path: Chemin du fichier créé
    """
    # TODO: Implémenter
    # Toujours extraire la page 0 vers "Programme.pdf"
    pass


def traiter_planche(pdf_doc, num_planche, planche_info, output_dir):
    """
    Traite une planche complète : compte les exercices et crée les fichiers appropriés.
    
    Logique de nommage :
    - 1 exercice  → P{num}.pdf
    - N exercices → P{num}-1.pdf, P{num}-2.pdf, ..., P{num}-N.pdf
    
    Pour le découpage avec plusieurs exercices :
    - Diviser équitablement le nombre de pages
    - pages_par_exercice = (end_page - start_page + 1) / nb_exercices
    
    Args:
        pdf_doc: Document PyMuPDF
        num_planche: Numéro de la planche
        planche_info: Dict {"start_page": X, "end_page": Y} (0-indexed)
        output_dir: Dossier de sortie (Path object)
    
    Returns:
        list[Path]: Liste des fichiers créés
    """
    # TODO: Implémenter
    pass


def afficher_progression(message, niveau="info"):
    """
    Affiche un message formaté avec des emojis.
    
    Args:
        message: Message à afficher
        niveau: "info", "success", "error", "warning"
    """
    emojis = {
        "info": "🔍",
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "process": "📝"
    }
    emoji = emojis.get(niveau, "ℹ️")
    print(f"{emoji} {message}")


def main():
    """Point d'entrée principal du script."""
    
    # 1. PARSER LES ARGUMENTS
    parser = argparse.ArgumentParser(
        description="Outil d'extraction automatique d'exercices depuis des planches PDF de colles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s Colles-6.pdf -m chimie -c PCSI -s 6
  %(prog)s Colles-Physique.pdf --matiere physique --classe MPSI --semaine 7
  %(prog)s input.pdf -m chimie -c PCSI -s 6 -o ./custom_output/
        """
    )
    
    parser.add_argument(
        "fichier_pdf",
        type=str,
        help="Chemin vers le fichier PDF à découper"
    )
    
    parser.add_argument(
        "-m", "--matiere",
        type=str,
        required=True,
        choices=["physique", "chimie"],
        help="Matière des colles (physique ou chimie)"
    )
    
    parser.add_argument(
        "-c", "--classe",
        type=str,
        required=True,
        choices=["MPSI", "PCSI"],
        help="Classe concernée (MPSI ou PCSI)"
    )
    
    parser.add_argument(
        "-s", "--semaine",
        type=int,
        required=True,
        help="Numéro de la semaine (ex: 6, 7, 8)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="./public/documents/exercices",
        help="Dossier de sortie (défaut: ./public/documents/exercices)"
    )
    
    args = parser.parse_args()
    
    # 2. VÉRIFIER L'EXISTENCE DU FICHIER
    fichier_pdf = Path(args.fichier_pdf)
    if not fichier_pdf.exists():
        afficher_progression(f"Le fichier {fichier_pdf} n'existe pas", "error")
        sys.exit(1)
    
    # 3. OUVRIR LE PDF
    try:
        pdf_doc = fitz.open(str(fichier_pdf))
        afficher_progression(f"Analyse du fichier : {fichier_pdf.name}", "info")
        afficher_progression(f"Pages totales : {len(pdf_doc)}", "info")
        print()  # Ligne vide pour la lisibilité
    except Exception as e:
        afficher_progression(f"Erreur lors de l'ouverture du PDF : {e}", "error")
        sys.exit(1)
    
    # 4. CRÉER LE DOSSIER DE SORTIE
    base_output = Path(args.output)
    dossier_final = base_output / args.matiere / f"Colles-{args.classe}-S{args.semaine}"
    dossier_final.mkdir(parents=True, exist_ok=True)
    
    # 5. EXTRAIRE LE PROGRAMME
    # TODO: Appeler extraire_programme()
    
    # 6. DÉTECTER LES PLANCHES
    # TODO: Appeler detecter_planches()
    
    # 7. TRAITER CHAQUE PLANCHE
    # TODO: Boucle sur les planches et appel de traiter_planche()
    
    # 8. AFFICHER LE RÉCAPITULATIF
    # TODO: Afficher un résumé avec le nombre de fichiers créés et le chemin
    
    # 9. FERMER LE PDF
    pdf_doc.close()


if __name__ == "__main__":
    main()
```

### 3. EXIGENCES CRITIQUES

**ABSOLUMENT RESPECTER** :

1. **Détection des planches** :
   - Pattern exact : `r"^Planche\s+(\d+)"` en multiline
   - Doit fonctionner même si le format LaTeX varie légèrement

2. **Comptage des exercices** :
   - NE PAS compter "Questions de cours"
   - Patterns : `r"Exercice\s*:\s*"` OU `r"Exercice\s+n°\d+\s*:\s*"`
   - Lever une exception si 0 exercice détecté

3. **Nommage des fichiers** :
   - 1 exercice : `P{n}.pdf` (exemple: `P1.pdf`)
   - N exercices : `P{n}-{i}.pdf` (exemple: `P1-1.pdf`, `P1-2.pdf`)
   - Programme : toujours `Programme.pdf`

4. **Gestion des pages** :
   - PyMuPDF utilise un indexing 0-based
   - Page 0 = Programme
   - Les planches commencent à partir de la page 1

5. **Messages utilisateur** :
   - Utiliser des emojis et des couleurs pour la clarté
   - Être verbeux : indiquer chaque étape
   - Exemple de sortie dans SPECIFICATIONS.md

### 4. TESTS À EFFECTUER

Une fois le script créé, teste avec :

```bash
# Test 1 : Fichier de test fourni
python colle_splitter.py tests/sample_files/Colles-6.pdf -m chimie -c PCSI -s 6

# Résultat attendu :
# public/documents/exercices/chimie/Colles-PCSI-S6/
# ├── Programme.pdf (1 page)
# ├── P1.pdf
# ├── P2.pdf
# └── P3.pdf
```

Vérifie que :
- [ ] 4 fichiers sont créés
- [ ] Les noms sont corrects
- [ ] Chaque PDF contient les bonnes pages
- [ ] Le Programme fait 1 page
- [ ] Les messages utilisateur sont clairs

### 5. GESTION DES ERREURS

Ajoute des `try/except` pour :
- Fichier PDF corrompu
- Aucune planche détectée
- Aucun exercice dans une planche
- Problème de permissions d'écriture

### 6. CODE QUALITY

- Utilise des **docstrings** pour chaque fonction
- Ajoute des **type hints** si possible
- Code **PEP 8 compliant**
- Commentaires explicatifs aux endroits complexes

### 7. CE QUI DOIT FONCTIONNER IMMÉDIATEMENT

Après ton implémentation, je dois pouvoir faire :

```bash
pip install -r requirements.txt
python colle_splitter.py Colles-6.pdf -m chimie -c PCSI -s 6
```

Et obtenir les 4 fichiers correctement nommés et découpés.

---

## RÉSUMÉ DES ÉTAPES

1. ✅ Lire `SPECIFICATIONS.md` COMPLÈTEMENT
2. ✅ Implémenter toutes les fonctions dans `colle_splitter.py`
3. ✅ Tester avec le fichier `Colles-6.pdf`
4. ✅ Corriger les bugs éventuels
5. ✅ Valider que les 4 fichiers sont corrects
6. ✅ Documenter les limites connues si nécessaire

---

## QUESTIONS AVANT DE COMMENCER

Si tu as besoin de clarifications sur :
- La structure du PDF LaTeX
- Les patterns de détection
- La logique de découpage
- Tout autre aspect

**POSE DES QUESTIONS** avant de commencer à coder !

---

## VALIDATION FINALE

Une fois terminé, vérifie que :
- [ ] Le script s'exécute sans erreur
- [ ] Les 4 fichiers sont créés au bon endroit
- [ ] Le nommage est correct (Programme.pdf, P1.pdf, P2.pdf, P3.pdf)
- [ ] Les messages utilisateur sont informatifs
- [ ] Le code est propre et documenté

---

**C'EST PARTI ! 🚀**

Commence par lire attentivement `SPECIFICATIONS.md`, puis implémente le script en suivant la structure fournie ci-dessus.
