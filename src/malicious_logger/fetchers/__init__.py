from malicious_logger.fetchers.alienvault import AlienVaultFetcher
from malicious_logger.fetchers.base import BaseFetcher, build_client
from malicious_logger.fetchers.openphish import OpenPhishFetcher
from malicious_logger.fetchers.urlhaus import URLHausFetcher

__all__ = [
    "BaseFetcher",
    "build_client",
    "URLHausFetcher",
    "AlienVaultFetcher",
    "OpenPhishFetcher",
]
