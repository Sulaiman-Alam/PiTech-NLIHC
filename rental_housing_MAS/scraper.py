import requests
from bs4 import BeautifulSoup


def scrape_url(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        # If bad response, skip safely
        if response.status_code != 200:
            return ""

        html = response.text

    except Exception as e:
        print(f"Scraper failed for {url}: {e}")
        return ""

    soup = BeautifulSoup(html, "html.parser")

    # remove junk
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    return text[:12000]