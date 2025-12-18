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

### Tests : pattern AAA + fixtures

- **1 test = 1 comportement**
- **Fixtures** avec `scope="module"` pour éviter les appels API répétés
- Nommer le test : `test_<ce_qui_est_testé>`

### Commits fréquents

- Committer **à chaque fonctionnalité qui MARCHE**
- Une fonctionnalité "marche" = les tests passent
- Pas de commit sans tests qui passent

### Communication

- Toujours proposer la prochaine feature avec une recommandation
- Ne pas demander "prochaine feature ?" sans suggestion

## Stack technique

- **Gestionnaire de projet** : `uv` (exclusivement)
  - Initialisation du projet : `uv init`
  - Gestion des dépendances : `uv add`
  - Lancement des scripts : `uv run`
  - Packaging : `uv build`
  - Publication : `uv publish`

### Dépendances

- **requests** : Client HTTP (simplicité > performance)
- **pytest** : Tests (dev dependency)

### Structure du code

```
src/pypubmed/
├── __init__.py      # Exports publics
├── client.py        # Classe PubMed (client principal)
├── export.py        # Fonctions d'export (JSON, CSV)
└── py.typed         # Support typing
```

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
uv run pytest              # Lancer les tests
uv build                   # Construire le package
uv publish                 # Publier sur PyPI
```

## Features

### Implémentées

- [x] `PubMed.search(query, min_date, max_date)` - Recherche avec filtres de date
- [x] `PubMed.fetch(ids)` - Récupérer les détails des articles
- [x] `PubMed.search_and_fetch(query)` - Recherche + fetch en un appel
- [x] `Article` dataclass - pmid, title, abstract, authors, journal, mesh_terms, keywords, doi, url, publication_date, journal_date
- [x] `SearchResult.count` - Nombre total de résultats
- [x] Rate limiting automatique (3 req/sec sans clé, 10 req/sec avec clé)
- [x] Support API key : `PubMed(api_key="...")`
- [x] Exceptions custom : `PubMedError`, `APIError`
- [x] Validation d'input : `fetch([])` → `ValueError`, `max_results <= 0` → `ValueError`
- [x] Sécurité XML avec `defusedxml`
- [x] Connection pooling avec `requests.Session()`
- [x] Retry automatique sur erreur réseau (3 retries, backoff exponentiel)
- [x] Cache optionnel : `PubMed(cache=True, cache_ttl=3600)`, `clear_cache()`
- [x] `Article.to_dict()` - Convertir un article en dictionnaire
- [x] Export JSON : `to_json(articles)`, `save_json(articles, path)`
- [x] Export CSV : `to_csv(articles)`, `save_csv(articles, path)` - UTF-8 BOM pour Excel/LibreOffice, listes jointes avec `; `
- [x] Import CSV : `from_csv(path)` - Réimporte les articles depuis un CSV exporté

### À implémenter

#### Priorité moyenne

- [ ] Tests unitaires avec mocking (fixtures mock dans conftest.py)

#### Priorité basse (pas besoin pour l'instant)

- [ ] Pagination (`search()` avec `offset`)
- [ ] Support async (httpx)

**Note:** Ne pas proposer ces features - l'utilisateur demandera si besoin.
