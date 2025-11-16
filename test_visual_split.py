#!/usr/bin/env python3
"""
Script de test pour le découpage visuel de pages PDF
"""

import fitz

def tester_decoupage_visuel():
    """Teste le découpage visuel sur un PDF de démonstration"""

    print("=" * 60)
    print("TEST DE DÉCOUPAGE VISUEL")
    print("=" * 60)

    # Créer un PDF de test avec 1 page
    test_pdf = fitz.open()
    page = test_pdf.new_page(width=595, height=842)  # Format A4

    # Ajouter du texte en haut (Exercice 1)
    page.insert_text((50, 100), "Exercice 1 - Chimie : Test exercice haut", fontsize=14)
    page.insert_text((50, 150), "Contenu de l'exercice 1...", fontsize=12)

    # Ajouter du texte en bas (Exercice 2)
    page.insert_text((50, 500), "Exercice 2 - Physique : Test exercice bas", fontsize=14)
    page.insert_text((50, 550), "Contenu de l'exercice 2...", fontsize=12)

    test_pdf.save("test_planche.pdf")
    test_pdf.close()

    print("✅ PDF de test créé : test_planche.pdf")
    print("   - Exercice 1 en haut")
    print("   - Exercice 2 en bas")

    # Maintenant découper ce PDF en 2 parties
    pdf_source = fitz.open("test_planche.pdf")

    # Partie haute (Exercice 1)
    page = pdf_source[0]
    rect = page.rect
    width = rect.width
    height = rect.height

    crop_rect_haut = fitz.Rect(0, 0, width, height / 2)
    pdf_haut = fitz.open()
    page_haut = pdf_haut.new_page(width=width, height=height/2)
    page_haut.show_pdf_page(page_haut.rect, pdf_source, 0, clip=crop_rect_haut)
    pdf_haut.save("test_P1-1.pdf")
    pdf_haut.close()

    print("\n✅ Partie haute découpée : test_P1-1.pdf")

    # Partie basse (Exercice 2)
    crop_rect_bas = fitz.Rect(0, height / 2, width, height)
    pdf_bas = fitz.open()
    page_bas = pdf_bas.new_page(width=width, height=height/2)
    page_bas.show_pdf_page(page_bas.rect, pdf_source, 0, clip=crop_rect_bas)
    pdf_bas.save("test_P1-2.pdf")
    pdf_bas.close()

    print("✅ Partie basse découpée : test_P1-2.pdf")

    pdf_source.close()

    print("\n" + "=" * 60)
    print("RÉSULTAT DU TEST")
    print("=" * 60)
    print("Vérifiez les fichiers générés :")
    print("  - test_planche.pdf (original avec 2 exercices)")
    print("  - test_P1-1.pdf (moitié haute = Exercice 1)")
    print("  - test_P1-2.pdf (moitié basse = Exercice 2)")
    print("=" * 60)

if __name__ == "__main__":
    tester_decoupage_visuel()
