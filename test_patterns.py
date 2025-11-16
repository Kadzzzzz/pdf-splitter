#!/usr/bin/env python3
"""
Script de test pour vérifier les patterns de détection d'exercices
"""

import re

def tester_pattern(texte_test):
    """Teste le pattern combiné sur un texte donné"""

    pattern_combine = r"""
        (?:Exercice\s+Bonus)                  |  # "Exercice Bonus" (NOUVEAU!)
        (?:Exercice\s+\d+\s*[-–]\s*\w+\s*:)  |  # "Exercice 1 - Chimie :" ou "Exercice 2 - Physique :"
        (?:Exercice\s+de\s+\w+\s*:)           |  # "Exercice de chimie :" ou "Exercice de physique :"
        (?:Exercice\s+n°\d+\s*:)              |  # "Exercice n°8 :"
        (?:Exercice\s+\d+\s*:)                |  # "Exercice 1:" (sans tiret ni matière)
        (?:Exercice\s*:)                      |  # "Exercice :" (avec deux-points)
        (?:^Exercice\s*$)                        # "Exercice" seul sur une ligne
    """

    matches = re.findall(pattern_combine, texte_test, re.VERBOSE | re.MULTILINE)
    return len(matches), matches


# Tests
print("=" * 60)
print("TEST 1: Planche avec 2 exercices (format avec tiret et matière)")
print("=" * 60)
texte1 = """
Planche 1
Questions de cours...

Exercice 1 - Chimie : Oxydation du dioxyde de soufre
Blabla...

Exercice 2 - Physique : Intensités et puissances
Blabla...
"""
nb, matches = tester_pattern(texte1)
print(f"Texte:\n{texte1}")
print(f"Résultat: {nb} exercice(s) détecté(s)")
print(f"Matches: {matches}")
print(f"✅ ATTENDU: 2 exercices" if nb == 2 else f"❌ ERREUR: attendu 2, obtenu {nb}")

print("\n" + "=" * 60)
print("TEST 2: Planche avec 1 seul exercice (format avec tiret)")
print("=" * 60)
texte2 = """
Planche 2
Questions de cours...

Exercice 1 - Chimie : Dosage du carbonate
Blabla...
"""
nb, matches = tester_pattern(texte2)
print(f"Texte:\n{texte2}")
print(f"Résultat: {nb} exercice(s) détecté(s)")
print(f"Matches: {matches}")
print(f"✅ ATTENDU: 1 exercice" if nb == 1 else f"❌ ERREUR: attendu 1, obtenu {nb}")

print("\n" + "=" * 60)
print("TEST 3: Planche avec 1 exercice (format simple avec deux-points)")
print("=" * 60)
texte3 = """
Planche 3
Questions de cours...

Exercice : Spectroscopie du diiode
Blabla...
"""
nb, matches = tester_pattern(texte3)
print(f"Texte:\n{texte3}")
print(f"Résultat: {nb} exercice(s) détecté(s)")
print(f"Matches: {matches}")
print(f"✅ ATTENDU: 1 exercice" if nb == 1 else f"❌ ERREUR: attendu 1, obtenu {nb}")

print("\n" + "=" * 60)
print("TEST 4: Planche avec format n°")
print("=" * 60)
texte4 = """
Planche 4

Exercice n°1 : Premier exercice
Blabla...

Exercice n°2 : Deuxième exercice
Blabla...
"""
nb, matches = tester_pattern(texte4)
print(f"Texte:\n{texte4}")
print(f"Résultat: {nb} exercice(s) détecté(s)")
print(f"Matches: {matches}")
print(f"✅ ATTENDU: 2 exercices" if nb == 2 else f"❌ ERREUR: attendu 2, obtenu {nb}")

print("\n" + "=" * 60)
print("TEST 5: Formats mixtes dans la même planche")
print("=" * 60)
texte5 = """
Planche 5

Exercice 1 - Chimie : Premier exercice avec tiret
Blabla...

Exercice : Deuxième exercice sans numéro
Blabla...
"""
nb, matches = tester_pattern(texte5)
print(f"Texte:\n{texte5}")
print(f"Résultat: {nb} exercice(s) détecté(s)")
print(f"Matches: {matches}")
print(f"✅ ATTENDU: 2 exercices" if nb == 2 else f"❌ ERREUR: attendu 2, obtenu {nb}")

print("\n" + "=" * 60)
print("TEST 6: Format 'Exercice de chimie/physique' (NOUVEAU!)")
print("=" * 60)
texte6 = """
Planche Bonus

Exercice de chimie : L'ammoniac
Blabla...

Exercice de physique : Vitesse de libération (P4)
Blabla...
"""
nb, matches = tester_pattern(texte6)
print(f"Texte:\n{texte6}")
print(f"Résultat: {nb} exercice(s) détecté(s)")
print(f"Matches: {matches}")
print(f"✅ ATTENDU: 2 exercices" if nb == 2 else f"❌ ERREUR: attendu 2, obtenu {nb}")

print("\n" + "=" * 60)
print("TEST 7: Format 'Exercice' seul sur une ligne (NOUVEAU!)")
print("=" * 60)
texte7 = """
Planche 2

Exercice
Le titre de l'exercice sur la ligne suivante
Blabla...
"""
nb, matches = tester_pattern(texte7)
print(f"Texte:\n{texte7}")
print(f"Résultat: {nb} exercice(s) détecté(s)")
print(f"Matches: {matches}")
print(f"✅ ATTENDU: 1 exercice" if nb == 1 else f"❌ ERREUR: attendu 1, obtenu {nb}")

print("\n" + "=" * 60)
print("TEST 8: Format 'Exercice Bonus' (NOUVEAU!)")
print("=" * 60)
texte8 = """
Exercice Bonus
Fil lesté entre deux poulies (P4)
Blabla...
"""
nb, matches = tester_pattern(texte8)
print(f"Texte:\n{texte8}")
print(f"Résultat: {nb} exercice(s) détecté(s)")
print(f"Matches: {matches}")
print(f"✅ ATTENDU: 1 exercice" if nb == 1 else f"❌ ERREUR: attendu 1, obtenu {nb}")

print("\n" + "=" * 60)
print("RÉSUMÉ")
print("=" * 60)
print("Tous les tests devraient afficher ✅")
