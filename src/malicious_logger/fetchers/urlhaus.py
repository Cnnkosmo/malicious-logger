from malicious_logger.fetchers.base import BaseFetcher


class URLHausFetcher(BaseFetcher, source_name="urlhaus"):
    source_url = "https://urlhaus.abuse.ch/downloads/csv_recent/"
