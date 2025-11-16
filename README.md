# Colle Splitter

Outil automatisé pour extraire et organiser les exercices de colles à partir de planches PDF LaTeX.

## Contexte

Cet outil permet de transformer automatiquement un fichier PDF contenant plusieurs planches de colles en fichiers individuels organisés, prêts à être publiés sur un site web.

## Structure attendue en sortie

```
public/documents/exercices/
├── physique/
│   └── Colles-MPSI-S7/
│       ├── Programme.pdf (première page uniquement)
│       ├── P1-1.pdf (Planche 1, Exercice 1)
│       ├── P1-2.pdf (Planche 1, Exercice 2)
│       ├── P2-1.pdf (Planche 2, Exercice 1)
│       ├── P2.pdf (Planche 2, exercice unique - pas de numéro)
│       └── ...
└── chimie/
    └── Colles-PCSI-S6/
        ├── Programme.pdf
        ├── P1.pdf
        ├── P2-1.pdf
        └── ...
```

## Fonctionnalités

- [x] Extraction automatique de la page "Programme"
- [x] Détection intelligente des planches
- [x] Extraction des exercices individuels
- [x] Nommage automatique selon la convention
- [x] Organisation dans la structure de dossiers appropriée

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
python colle_splitter.py <fichier_pdf> --matiere <physique|chimie> --classe <MPSI|PCSI> --semaine <numero>
```

## Développement

Voir `SPECIFICATIONS.md` pour les détails techniques complets.
