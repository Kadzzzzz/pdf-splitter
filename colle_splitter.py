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
    Détecte toutes les planches dans le PDF (y compris Planche Bonus)

    Args:
        pdf_doc: Document PDF ouvert avec fitz

    Returns:
        dict: {numéro_planche: {"start_page": X, "end_page": Y}}
    """
    planches = {}
    pattern_planche_num = r"^Planche\s+(\d+)"
    pattern_planche_bonus = r"^Planche\s+Bonus"

    for page_num in range(len(pdf_doc)):
        texte = extraire_texte_page(pdf_doc, page_num)

        # Chercher "Planche X" ou "Planche Bonus" en début de page
        for ligne in texte.split('\n'):
            ligne_strip = ligne.strip()

            # Vérifier si c'est "Planche Bonus" (doit être vérifié AVANT le pattern numérique)
            # Insensible à la casse
            if re.match(pattern_planche_bonus, ligne_strip, re.IGNORECASE):
                # Toujours attribuer le numéro 4 à la Planche Bonus
                num_planche = 4
                planches[num_planche] = {
                    "start_page": page_num,
                    "end_page": page_num,
                    "nom": "Bonus"
                }
                break

            # Vérifier si c'est "Planche X" (numérique)
            match = re.match(pattern_planche_num, ligne_strip)
            if match:
                num_planche = int(match.group(1))
                planches[num_planche] = {
                    "start_page": page_num,
                    "end_page": page_num,
                    "nom": str(num_planche)
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
        (?:Exercice\s+de\s+\w+\s*:)           |  # "Exercice de chimie :" ou "Exercice de physique :"
        (?:Exercice\s+n°\d+\s*:)              |  # "Exercice n°8 :"
        (?:Exercice\s+\d+\s*:)                |  # "Exercice 1:" (sans tiret ni matière)
        (?:Exercice\s*:)                      |  # "Exercice :" (avec deux-points)
        (?:^Exercice\s*$)                        # "Exercice" seul sur une ligne (NOUVEAU!)
    """

    # Compter toutes les occurrences en une seule passe
    matches = re.findall(pattern_combine, texte_complet, re.VERBOSE | re.MULTILINE)
    nb_exercices = len(matches)

    # Debug : afficher ce qui a été trouvé
    if nb_exercices > 0 and matches:
        print(f"   🔍 Exercices détectés : {matches}")

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


def detecter_positions_exercices(pdf_doc, page_num):
    """
    Détecte les positions Y des exercices dans une page

    Args:
        pdf_doc: Document PDF source
        page_num: Numéro de la page (0-indexed)

    Returns:
        list: Liste des positions Y (coordonnées verticales) où commencent les exercices
    """
    page = pdf_doc[page_num]
    positions = []

    # Chercher tous les patterns possibles d'exercices
    # L'ordre est important : les plus spécifiques d'abord pour éviter les faux positifs
    patterns_recherche = [
        "Exercice 1 -",
        "Exercice 2 -",
        "Exercice 3 -",
        "Exercice de chimie",      # Chercher d'abord les formes spécifiques
        "Exercice de physique",     # avant les formes génériques
        "Exercice de biologie",
        "Exercice de mathématiques",
        "Exercice n°1",
        "Exercice n°2",
        "Exercice n°3",
        "Exercice 1:",
        "Exercice 2:",
        "Exercice 3:",
        "Exercice :",
        "Exercice",                 # En dernier recours, chercher juste "Exercice"
    ]

    for pattern in patterns_recherche:
        # Chercher le texte dans la page (insensible à la casse)
        text_instances = page.search_for(pattern, flags=fitz.TEXT_DEHYPHENATE)

        for inst in text_instances:
            # inst est un fitz.Rect qui contient les coordonnées
            # On garde la position Y (verticale) du haut du rectangle
            y_position = inst.y0

            # Éviter les doublons (si plusieurs patterns matchent au même endroit)
            # On considère que 2 positions à moins de 10 points sont identiques
            est_doublon = False
            for pos in positions:
                if abs(pos - y_position) < 10:
                    est_doublon = True
                    break

            if not est_doublon:
                positions.append(y_position)

    # Trier les positions du haut vers le bas
    positions.sort()

    # Debug : afficher les positions trouvées
    if positions:
        print(f"   📍 Positions Y détectées : {[round(p, 1) for p in positions]}")

    return positions


def decouper_page_verticalement(pdf_doc, page_num, nb_parties, partie_index, output_path):
    """
    Découpe visuellement une page PDF en plusieurs parties verticales (haut/bas)
    en utilisant les positions réelles des exercices détectés

    Args:
        pdf_doc: Document PDF source
        page_num: Numéro de la page à découper (0-indexed)
        nb_parties: Nombre de parties (2 = moitié haute et moitié basse)
        partie_index: Index de la partie à extraire (0 = première partie/haut, 1 = deuxième partie/bas, etc.)
        output_path: Chemin de sortie du PDF
    """
    page = pdf_doc[page_num]
    rect = page.rect  # Rectangle de la page complète
    width = rect.width
    height = rect.height

    # Détecter les positions réelles des exercices
    positions_exercices = detecter_positions_exercices(pdf_doc, page_num)

    # Déterminer les coordonnées de découpe
    if len(positions_exercices) >= nb_parties:
        # On a détecté les positions des exercices, on les utilise !
        if partie_index == 0:
            # Premier exercice : du haut de la page jusqu'au début du 2ème exercice
            y0 = 0
            y1 = positions_exercices[1] if len(positions_exercices) > 1 else height
        elif partie_index < nb_parties - 1:
            # Exercice du milieu : du début de cet exercice au début du suivant
            y0 = positions_exercices[partie_index]
            y1 = positions_exercices[partie_index + 1]
        else:
            # Dernier exercice : du début de cet exercice jusqu'à la fin de la page
            y0 = positions_exercices[partie_index]
            y1 = height
    else:
        # Fallback : découpage égal si on n'a pas trouvé les positions
        print(f"   ⚠️  Positions exactes non détectées, utilisation du découpage équitable")
        hauteur_partie = height / nb_parties
        y0 = partie_index * hauteur_partie
        y1 = (partie_index + 1) * hauteur_partie

    crop_rect = fitz.Rect(0, y0, width, y1)
    hauteur_partie = y1 - y0

    # Créer un nouveau PDF avec la partie découpée
    nouveau_pdf = fitz.open()
    nouvelle_page = nouveau_pdf.new_page(width=width, height=hauteur_partie)

    # Afficher la portion de la page source sur la nouvelle page
    nouvelle_page.show_pdf_page(
        nouvelle_page.rect,  # Destination (toute la nouvelle page)
        pdf_doc,             # Document source
        page_num,            # Numéro de page source
        clip=crop_rect       # Zone à copier (la partie découpée)
    )

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
    Traite une planche complète avec découpage visuel des exercices :
    1. Compte les exercices
    2. Découpe visuellement la page selon le nombre d'exercices
    3. Sauvegarde avec la bonne convention de nommage

    Args:
        pdf_doc: Document PDF source
        num_planche: Numéro de la planche
        planche_info: Dict avec start_page, end_page et nom
        output_dir: Répertoire de sortie
    """
    start_page = planche_info["start_page"]
    end_page = planche_info["end_page"]
    nom_planche = planche_info.get("nom", str(num_planche))

    # Compter les exercices
    nb_exercices = compter_exercices(pdf_doc, start_page, end_page)

    print(f"\n📝 Traitement Planche {nom_planche} :")

    if nb_exercices == 0:
        print(f"❌ Erreur : Aucun exercice détecté dans la planche (pages {start_page + 1} à {end_page + 1})")
        return 0

    nombre_pages = end_page - start_page + 1

    if nb_exercices == 1:
        # Un seul exercice : extraire toute(s) la/les page(s) de la planche
        output_path = output_dir / f"P{num_planche}.pdf"
        extraire_pages(pdf_doc, start_page, end_page, str(output_path))
        print(f"   └─ 1 exercice détecté → P{num_planche}.pdf ✅")
        return 1
    else:
        # Plusieurs exercices : découper visuellement la page
        fichiers_crees = 0

        if nombre_pages == 1:
            # Cas typique : tous les exercices sont sur UNE SEULE page
            # → Découper visuellement cette page en N parties verticales
            for i in range(nb_exercices):
                output_path = output_dir / f"P{num_planche}-{i+1}.pdf"
                decouper_page_verticalement(
                    pdf_doc,
                    start_page,      # La page unique à découper
                    nb_exercices,    # Nombre de parties
                    i,               # Index de la partie (0 = haut, 1 = bas, etc.)
                    str(output_path)
                )
                fichiers_crees += 1

            print(f"   └─ {nb_exercices} exercices détectés (sur 1 page) → P{num_planche}-1.pdf à P{num_planche}-{nb_exercices}.pdf ✅")
        else:
            # Cas rare : la planche s'étend sur plusieurs pages
            # → Diviser équitablement les pages entre les exercices
            pages_par_exercice = nombre_pages / nb_exercices

            for i in range(nb_exercices):
                ex_start = int(start_page + i * pages_par_exercice)
                ex_end = int(start_page + (i + 1) * pages_par_exercice - 1)

                # Gérer le dernier exercice (s'assurer d'aller jusqu'à la fin)
                if i == nb_exercices - 1:
                    ex_end = end_page

                output_path = output_dir / f"P{num_planche}-{i+1}.pdf"
                extraire_pages(pdf_doc, ex_start, ex_end, str(output_path))
                fichiers_crees += 1

            print(f"   └─ {nb_exercices} exercices détectés (sur {nombre_pages} pages) → P{num_planche}-1.pdf à P{num_planche}-{nb_exercices}.pdf ✅")

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
