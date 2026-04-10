from ddgs import DDGS

def discovery_agent(query, max_results=5):
    urls = []

    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=max_results)

        for r in results:
            if isinstance(r, dict):
                url = r.get("href")
                if url:
                    urls.append(url)

    return urls