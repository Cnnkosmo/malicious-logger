from malicious_logger.fetchers.base import BaseFetcher


class OpenPhishFetcher(BaseFetcher, source_name="openphish"):
    source_url = "https://openphish.com/feed.txt"
