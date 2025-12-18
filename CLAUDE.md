# CLAUDE.md - Instructions pour le projet PyPubMed

## Objectif du projet

Créer un package Python **simple, rapide et efficace** avec un seul objectif :
**Permettre d'utiliser l'API PubMed depuis Python.**

## Principes directeurs

- **Simplicité** : Une seule responsabilité, pas de bloat
- **Rapidité** : Performance et efficacité
- **Efficacité** : API claire et intuitive

## Workflow de développement

### TDD (Test-Driven Development)

1. **Écrire le test** pour la feature
2. **Exécuter le test** : `uv run pytest` → doit **FAIL**
3. **Écrire le code** pour faire passer le test
4. **Réexécuter le test** : `uv run pytest` → doit **PASS**

### Commits fréquents

- Committer **à chaque fonctionnalité qui MARCHE**
- Une fonctionnalité "marche" = les tests passent
- Pas de commit sans tests qui passent

## Stack technique

- **Gestionnaire de projet** : `uv` (exclusivement)
  - Initialisation du projet : `uv init`
  - Gestion des dépendances : `uv add`
  - Lancement des scripts : `uv run`
  - Packaging : `uv build`
  - Publication : `uv publish`

## API PubMed

- Base URL : https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
- Documentation : https://www.ncbi.nlm.nih.gov/books/NBK25500/
- Endpoints principaux :
  - `esearch.fcgi` : Recherche d'articles
  - `efetch.fcgi` : Récupération des détails
  - `einfo.fcgi` : Informations sur la base de données

## Commandes uv essentielles

```bash
uv init                    # Initialiser le projet
uv add <package>           # Ajouter une dépendance
uv add --dev <package>     # Ajouter une dépendance de dev
uv run <script>            # Exécuter un script
uv run python -m pytest    # Lancer les tests
uv build                   # Construire le package
uv publish                 # Publier sur PyPI
```
