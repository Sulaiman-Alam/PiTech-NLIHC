from ddgs import DDGS

with DDGS() as ddgs:
    results = ddgs.text("NYC rental assistance", max_results=5)
    for r in results:
        print(r)