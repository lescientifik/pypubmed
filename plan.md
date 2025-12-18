# Plan du projet PyPubMed

## Vue d'ensemble

Package Python minimaliste pour interagir avec l'API PubMed (NCBI E-utilities).

## Phase 1 : Setup du projet

- [x] Créer CLAUDE.md
- [x] Créer plan.md
- [ ] Initialiser le projet avec `uv init`
- [ ] Configurer pyproject.toml
- [ ] Créer la structure de fichiers

## Phase 2 : Structure du package

```
pypubmed/
├── pyproject.toml
├── README.md
├── CLAUDE.md
├── plan.md
├── src/
│   └── pypubmed/
│       ├── __init__.py
│       ├── client.py      # Client HTTP principal
│       ├── models.py      # Modèles de données (dataclasses)
│       └── exceptions.py  # Exceptions personnalisées
└── tests/
    └── test_client.py
```

## Phase 3 : Fonctionnalités core

### Client PubMed
- [ ] Classe `PubMed` - client principal
- [ ] Méthode `search()` - recherche d'articles (esearch)
- [ ] Méthode `fetch()` - récupération des détails (efetch)
- [ ] Méthode `info()` - informations sur la base (einfo)

### Modèles de données
- [ ] `Article` - représentation d'un article
- [ ] `SearchResult` - résultat de recherche

### Gestion des erreurs
- [ ] `PubMedError` - exception de base
- [ ] `RateLimitError` - limite de requêtes atteinte
- [ ] `APIError` - erreur de l'API

## Phase 4 : Dépendances minimales

- `httpx` : Client HTTP moderne et async-compatible
- `pydantic` ou dataclasses natives (à décider)

## Phase 5 : Tests et qualité

- [ ] Tests unitaires avec pytest
- [ ] Tests d'intégration (optionnel)
- [ ] Type hints complets

## Phase 6 : Publication

- [ ] Build avec `uv build`
- [ ] Publication sur PyPI avec `uv publish`

## API souhaitée (exemple d'usage)

```python
from pypubmed import PubMed

# Initialisation
pubmed = PubMed()

# Recherche
results = pubmed.search("cancer treatment", max_results=10)

# Récupération des détails
articles = pubmed.fetch(results.ids)

for article in articles:
    print(article.title)
    print(article.authors)
    print(article.abstract)
```

## Questions ouvertes

1. Support async ? (httpx le permet facilement)
2. Caching des résultats ?
3. API key PubMed (optionnelle mais recommandée) ?
