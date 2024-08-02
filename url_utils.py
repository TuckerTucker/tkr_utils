# tkr_utils/url_utils.py

from urllib.parse import urlparse, urljoin, urlunparse
from typing import Optional, Tuple, List
import re
import os
from tkr_utils import setup_logging, logs_and_exceptions
from tkr_utils.app_paths import AppPaths
from tkr_utils.extract_url import extract_url  # Assuming extract_url is defined here

logger = setup_logging(__file__)

class URLUtils:
    @staticmethod
    @logs_and_exceptions(logger)
    def parse_url(url: str) -> Tuple[str, str, str, str, str, str]:
        parsed = urlparse(url)
        return parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, parsed.fragment

    @staticmethod
    @logs_and_exceptions(logger)
    def is_valid_url(url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    @staticmethod
    @logs_and_exceptions(logger)
    def normalize_url(url: str) -> str:
        parsed = urlparse(url)
        if not parsed.scheme:
            url = f"http://{url}"
            parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        path = parsed.path.rstrip('/')
        if ':' in netloc:
            hostname, port = netloc.split(':')
            if (parsed.scheme == 'http' and port == '80') or (parsed.scheme == 'https' and port == '443'):
                netloc = hostname
        normalized = urlunparse((parsed.scheme, netloc, path, '', parsed.query, ''))
        return normalized

    @staticmethod
    @logs_and_exceptions(logger)
    def get_domain(url: str) -> Optional[str]:
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except ValueError:
            return None

    @staticmethod
    @logs_and_exceptions(logger)
    def is_same_domain(url1: str, url2: str) -> bool:
        domain1 = URLUtils.get_domain(url1)
        domain2 = URLUtils.get_domain(url2)
        return domain1 == domain2 if domain1 and domain2 else False

    @staticmethod
    @logs_and_exceptions(logger)
    def join_url(base: str, url: str) -> str:
        return urljoin(base, url)

    @staticmethod
    @logs_and_exceptions(logger)
    def get_url_path_segments(url: str) -> List[str]:
        parsed = urlparse(url)
        return [segment for segment in parsed.path.split('/') if segment]

    @staticmethod
    @logs_and_exceptions(logger)
    def url_to_filename(url: str) -> str:
        url = re.sub(r'^https?://(www\.)?', '', url)
        filename = re.sub(r'[^a-zA-Z0-9]', '_', url)
        filename = re.sub(r'_+', '_', filename)
        filename = filename.strip('_')
        return filename

    @staticmethod
    @logs_and_exceptions(logger)
    def save_dir_info(url: str) -> str:
        filename = URLUtils.url_to_filename(url)
        save_dir = os.path.join(AppPaths.PAGES_DIR, filename)
        os.makedirs(save_dir, exist_ok=True)
        logger.info(f"Created save directory for URL {url}: {save_dir}")
        return save_dir

    @staticmethod
    @logs_and_exceptions(logger)
    def extract_url(text: str) -> Optional[str]:
        return extract_url(text)

    @staticmethod
    @logs_and_exceptions(logger)
    def url_to_dirname(url: str) -> str:
        parsed_url = urlparse(url)
        dirname = parsed_url.path.replace('www.', '').replace('.', '_')
        logger.info(f"The parsed url: {parsed_url}, The dirname: {dirname}")
        return dirname