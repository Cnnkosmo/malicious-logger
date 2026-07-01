from malicious_logger.fetchers.base import BaseFetcher


class AlienVaultFetcher(BaseFetcher, source_name="alienvault"):
    source_url = "http://reputation.alienvault.com/reputation.data"  # pyright: ignore[reportUnannotatedClassAttribute]
