import pytest

from pypubmed import PubMedError, APIError


def test_pubmed_error_is_exception():
    assert issubclass(PubMedError, Exception)


def test_api_error_inherits_pubmed_error():
    assert issubclass(APIError, PubMedError)


def test_api_error_can_be_raised():
    with pytest.raises(PubMedError):
        raise APIError("test error")
