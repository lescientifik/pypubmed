# Code Review - PyPubMed

**Date:** 2025-12-18
**Version:** 0.1.0
**Score:** 8/10

---

## Résumé

| Catégorie | Score | Notes |
|-----------|-------|-------|
| Architecture | 9/10 | Propre, bien structuré |
| Gestion d'erreurs | 8/10 | Exceptions custom, retry, validation |
| Type Safety | 9/10 | Type hints, py.typed |
| Couverture Tests | 7/10 | Mocking ajouté, quelques cas manquants |
| Sécurité | 8/10 | defusedxml, timeout manquant |
| Performance | 7/10 | Session, cache, mais pas d'async |
| Documentation | 6/10 | Docstrings manquantes |

---

## Points Forts

- Architecture propre avec séparation des responsabilités
- Type hints Python 3.12+ (`list[str]`, `str | None`)
- Exceptions custom (`PubMedError`, `APIError`)
- Sécurité XML avec `defusedxml`
- Connection pooling avec `requests.Session()`
- Retry avec backoff exponentiel (3 retries)
- Validation des inputs (`fetch([])`, `max_results <= 0`)
- Cache avec TTL et fetch partiel
- 55 tests dont tests mockés rapides

---

## Recommandations

### Haute Priorité

#### 1. Ajouter timeout aux requêtes
```python
# Actuellement (dangereux - peut bloquer indéfiniment)
response = self._session.get(url, params=params)

# Recommandé
response = self._session.get(url, params=params, timeout=(5, 30))  # (connect, read)
```

#### 2. Ajouter docstrings aux méthodes publiques
```python
def search(
    self,
    query: str,
    max_results: int = 20,
    min_date: str | None = None,
    max_date: str | None = None,
) -> SearchResult:
    """Search PubMed for articles matching a query.

    Args:
        query: Search terms (PubMed query syntax supported).
        max_results: Maximum number of IDs to return (default 20).
        min_date: Minimum publication date (format: YYYY/MM/DD).
        max_date: Maximum publication date (format: YYYY/MM/DD).

    Returns:
        SearchResult with list of PMIDs and total count.

    Raises:
        ValueError: If max_results <= 0.
        APIError: If the PubMed API returns an error.
    """
```

#### 3. Limiter fetch() à 200 IDs max
```python
def fetch(self, ids: list[str]) -> list[Article]:
    if not ids:
        raise ValueError("ids cannot be empty")
    if len(ids) > 200:
        raise ValueError("Cannot fetch more than 200 IDs at once (PubMed limit)")
```

### Priorité Moyenne

#### 4. Valider le format des dates
```python
import re
DATE_PATTERN = re.compile(r'^\d{4}/\d{2}/\d{2}$')

if min_date and not DATE_PATTERN.match(min_date):
    raise ValueError("min_date must be in YYYY/MM/DD format")
```

#### 5. Ajouter paramètre `tool` aux requêtes
```python
# Recommandé par NCBI pour identifier l'application
params["tool"] = "pypubmed"
```

#### 6. Tests pour cas limites manquants
- Article sans abstract
- Article sans DOI
- Article sans publication_date
- XML malformé
- Comportement avec API key

#### 7. Gestion silencieuse des erreurs de date
```python
# Actuellement: mois invalide -> Janvier silencieusement
month = months.get(month.lower()[:3], 1)

# Recommandé: logger un warning ou lever une erreur
```

### Basse Priorité

#### 8. Chunking automatique pour batches > 200 IDs
```python
def fetch(self, ids: list[str]) -> list[Article]:
    if len(ids) > 200:
        # Découper en chunks de 200 et combiner les résultats
        chunks = [ids[i:i+200] for i in range(0, len(ids), 200)]
        return [article for chunk in chunks for article in self._fetch_chunk(chunk)]
```

#### 9. Support pagination dans search()
```python
def search(self, query: str, max_results: int = 20, offset: int = 0) -> SearchResult:
    params["retstart"] = offset
```

#### 10. Parsing d'abstract incomplet
```python
# Actuellement: ne gère pas les balises imbriquées
abstract = " ".join(part.text or "" for part in abstract_parts)

# Les labels des abstracts structurés (Background, Methods, etc.) sont perdus
```

---

## Tests Manquants

| Test | Description |
|------|-------------|
| `test_fetch_with_api_key` | Vérifier comportement avec API key |
| `test_article_without_abstract` | Article sans abstract |
| `test_article_without_doi` | Article sans DOI |
| `test_article_without_publication_date` | Article sans date électronique |
| `test_fetch_malformed_xml` | Réponse XML invalide |
| `test_search_invalid_date_format` | Format de date invalide |
| `test_fetch_over_200_ids` | Plus de 200 IDs |

---

## Fichiers Analysés

- `src/pypubmed/client.py` - Code principal
- `src/pypubmed/__init__.py` - Exports
- `tests/*.py` - 55 tests
- `pyproject.toml` - Configuration
- `README.md` - Documentation
- `LICENSE` - MIT
