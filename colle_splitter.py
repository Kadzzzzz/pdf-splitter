#!/usr/bin/env python3
"""
Colle Splitter - Automatisation du découpage de planches d'exercices
Auteur : Jeremy Luccioni
Date : 16 novembre 2025
"""

import fitz  # PyMuPDF
import argparse
import re
from pathlib import Path
import sys


def extraire_texte_page(pdf_doc, page_num):
    """
    Extrait le texte d'une page donnée

    Args:
        pdf_doc: Document PDF ouvert avec fitz
        page_num: Numéro de la page (0-indexed)

    Returns:
        str: Texte extrait de la page
    """
    page = pdf_doc[page_num]
    return page.get_text()


def detecter_planches(pdf_doc):
    """
    Détecte toutes les planches dans le PDF

    Args:
        pdf_doc: Document PDF ouvert avec fitz

    Returns:
        dict: {numéro_planche: {"start_page": X, "end_page": Y}}
    """
    planches = {}
    pattern_planche = r"^Planche\s+(\d+)"

    for page_num in range(len(pdf_doc)):
        texte = extraire_texte_page(pdf_doc, page_num)

        # Chercher "Planche X" en début de page
        for ligne in texte.split('\n'):
            match = re.match(pattern_planche, ligne.strip())
            if match:
                num_planche = int(match.group(1))
                planches[num_planche] = {
                    "start_page": page_num,
                    "end_page": page_num  # Sera ajusté plus tard
                }
                break

    # Ajuster les end_page en fonction de la planche suivante
    nums_planches = sorted(planches.keys())
    for i, num in enumerate(nums_planches):
        if i < len(nums_planches) - 1:
            # La planche se termine juste avant la prochaine
            planches[num]["end_page"] = planches[nums_planches[i + 1]]["start_page"] - 1
        else:
            # Dernière planche : va jusqu'à la fin du document
            planches[num]["end_page"] = len(pdf_doc) - 1

    return planches


def compter_exercices(pdf_doc, start_page, end_page):
    """
    Compte le nombre d'exercices dans une planche

    Args:
        pdf_doc: Document PDF ouvert avec fitz
        start_page: Page de début (0-indexed)
        end_page: Page de fin (0-indexed, inclusive)

    Returns:
        int: Nombre d'exercices détectés
    """
    # Extraire tout le texte de la planche
    texte_complet = ""
    for page_num in range(start_page, end_page + 1):
        texte_complet += extraire_texte_page(pdf_doc, page_num)

    # Pattern combiné pour détecter tous les formats d'exercices
    # Utilise des alternatives (|) pour tester tous les formats
    # L'ordre est important : patterns les plus spécifiques d'abord
    pattern_combine = r"""
        (?:Exercice\s+\d+\s*[-–]\s*\w+\s*:)  |  # "Exercice 1 - Chimie :" ou "Exercice 2 - Physique :"
        (?:Exercice\s+n°\d+\s*:)              |  # "Exercice n°8 :"
        (?:Exercice\s+\d+\s*:)                |  # "Exercice 1:" (sans tiret ni matière)
        (?:Exercice\s*:)                         # "Exercice :" (format minimal)
    """

    # Compter toutes les occurrences en une seule passe
    matches = re.findall(pattern_combine, texte_complet, re.VERBOSE | re.MULTILINE)
    nb_exercices = len(matches)

    return nb_exercices


def extraire_pages(pdf_doc, start_page, end_page, output_path):
    """
    Extrait un ensemble de pages et sauvegarde dans un nouveau PDF

    Args:
        pdf_doc: Document PDF source
        start_page: Page de début (0-indexed)
        end_page: Page de fin (0-indexed, inclusive)
        output_path: Chemin de sortie du PDF
    """
    nouveau_pdf = fitz.open()
    nouveau_pdf.insert_pdf(pdf_doc, from_page=start_page, to_page=end_page)
    nouveau_pdf.save(output_path)
    nouveau_pdf.close()


def extraire_programme(pdf_doc, output_dir):
    """
    Extrait la première page (Programme) et sauvegarde

    Args:
        pdf_doc: Document PDF source
        output_dir: Répertoire de sortie
    """
    programme_path = output_dir / "Programme.pdf"
    extraire_pages(pdf_doc, 0, 0, str(programme_path))
    print(f"\n✅ Programme extrait : Programme.pdf")


def traiter_planche(pdf_doc, num_planche, planche_info, output_dir):
    """
    Traite une planche complète :
    1. Compte les exercices
    2. Découpe selon le nombre
    3. Sauvegarde avec la bonne convention de nommage

    Args:
        pdf_doc: Document PDF source
        num_planche: Numéro de la planche
        planche_info: Dict avec start_page et end_page
        output_dir: Répertoire de sortie
    """
    start_page = planche_info["start_page"]
    end_page = planche_info["end_page"]

    # Compter les exercices
    nb_exercices = compter_exercices(pdf_doc, start_page, end_page)

    print(f"\n📝 Traitement Planche {num_planche} :")

    if nb_exercices == 0:
        print(f"❌ Erreur : Aucun exercice détecté dans la planche (pages {start_page} à {end_page})")
        return 0

    nombre_pages = end_page - start_page + 1

    if nb_exercices == 1:
        # Un seul exercice : PX.pdf
        output_path = output_dir / f"P{num_planche}.pdf"
        extraire_pages(pdf_doc, start_page, end_page, str(output_path))
        print(f"   └─ 1 exercice détecté → P{num_planche}.pdf ✅")
        return 1
    else:
        # Plusieurs exercices : PX-1.pdf, PX-2.pdf, etc.
        pages_par_exercice = nombre_pages / nb_exercices
        fichiers_crees = 0

        for i in range(nb_exercices):
            # Calculer les pages pour cet exercice
            ex_start = int(start_page + i * pages_par_exercice)
            ex_end = int(start_page + (i + 1) * pages_par_exercice - 1)

            # Gérer le dernier exercice (s'assurer d'aller jusqu'à la fin)
            if i == nb_exercices - 1:
                ex_end = end_page

            output_path = output_dir / f"P{num_planche}-{i+1}.pdf"
            extraire_pages(pdf_doc, ex_start, ex_end, str(output_path))
            fichiers_crees += 1

        print(f"   └─ {nb_exercices} exercices détectés → P{num_planche}-1.pdf à P{num_planche}-{nb_exercices}.pdf ✅")
        return fichiers_crees


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="Découpe automatique de planches d'exercices de colles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation :
  python colle_splitter.py Colles-6.pdf -m chimie -c PCSI -s 6
  python colle_splitter.py S7_MPSI.pdf -m physique -c MPSI -s 7 -o ./output/
        """
    )

    # Arguments positionnels
    parser.add_argument("fichier_pdf", help="Chemin vers le fichier PDF à découper")

    # Arguments obligatoires
    parser.add_argument("-m", "--matiere", required=True, choices=["physique", "chimie"],
                        help="Matière (physique ou chimie)")
    parser.add_argument("-c", "--classe", required=True, choices=["MPSI", "PCSI"],
                        help="Classe (MPSI ou PCSI)")
    parser.add_argument("-s", "--semaine", required=True, type=int,
                        help="Numéro de la semaine")

    # Arguments optionnels
    parser.add_argument("-o", "--output", default="./public/documents/exercices/",
                        help="Dossier de sortie (défaut: ./public/documents/exercices/)")

    args = parser.parse_args()

    # Vérifier que le fichier PDF existe
    fichier_pdf = Path(args.fichier_pdf)
    if not fichier_pdf.exists():
        print(f"❌ Erreur : Le fichier '{args.fichier_pdf}' n'existe pas")
        sys.exit(1)

    # Ouvrir le PDF
    print(f"🔍 Analyse du fichier : {fichier_pdf.name}")
    try:
        pdf_doc = fitz.open(str(fichier_pdf))
    except Exception as e:
        print(f"❌ Erreur lors de l'ouverture du PDF : {e}")
        sys.exit(1)

    print(f"🔍 Pages totales : {len(pdf_doc)}")

    # Créer le dossier de sortie
    base_output = Path(args.output)
    dossier_final = base_output / args.matiere / f"Colles-{args.classe}-S{args.semaine}"
    dossier_final.mkdir(parents=True, exist_ok=True)

    # Extraire le programme (page 1)
    extraire_programme(pdf_doc, dossier_final)
    fichiers_crees = 1

    # Détecter les planches
    print(f"\n🔍 Détection des planches...")
    planches = detecter_planches(pdf_doc)

    if not planches:
        print("❌ Erreur : Aucune planche détectée dans le PDF")
        pdf_doc.close()
        sys.exit(1)

    # Afficher les planches détectées
    for num in sorted(planches.keys()):
        start = planches[num]["start_page"]
        print(f"🔍    {'├' if num < max(planches.keys()) else '└'}─ Planche {num} détectée (page {start + 1})")

    # Traiter chaque planche
    for num in sorted(planches.keys()):
        fichiers_crees += traiter_planche(pdf_doc, num, planches[num], dossier_final)

    # Fermer le PDF
    pdf_doc.close()

    # Récapitulatif
    print(f"\n✅ Terminé ! {fichiers_crees} fichiers créés dans :")
    print(f"✅    → {dossier_final}")


if __name__ == "__main__":
    main()
