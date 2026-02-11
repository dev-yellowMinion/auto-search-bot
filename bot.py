import os, requests, re
from collections import Counter

TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

SEARCH_QUERY = 'type:user location:"United States" language:Python'
USERS_URL = "https://api.github.com/search/users"
REPOS_URL = "https://api.github.com/users/{}/repos"

AI_KEYWORDS = {
    "machine learning", "deep learning", "ai", "llm",
    "tensorflow", "pytorch", "openai", "nlp"
}
FULLSTACK_KEYWORDS = {
    "react", "next.js", "vue", "node", "express",
    "django", "fastapi", "typescript"
}

def score_user(repos):
    score = 0
    tags = Counter()

    for r in repos:
        text = (r.get("description") or "").lower()
        topics = " ".join(r.get("topics", [])).lower()

        for kw in AI_KEYWORDS:
            if kw in text or kw in topics:
                score += 3
                tags["AI"] += 1

        for kw in FULLSTACK_KEYWORDS:
            if kw in text or kw in topics:
                score += 2
                tags["Full-Stack"] += 1

        score += min(r.get("stargazers_count", 0), 10) * 0.1

    return score, tags

def main():
    users = requests.get(
        USERS_URL, headers=HEADERS, params={"q": SEARCH_QUERY, "per_page": 20}
    ).json()["items"]

    results = []

    for u in users:
        repos = requests.get(
            REPOS_URL.format(u["login"]),
            headers=HEADERS,
            params={"per_page": 30, "sort": "updated"}
        ).json()

        score, tags = score_user(repos)

        if score >= 8:  # recruiter-quality threshold
            results.append({
                "login": u["login"],
                "url": u["html_url"],
                "score": round(score, 1),
                "tags": ", ".join(tags.keys())
            })

    results.sort(key=lambda x: x["score"], reverse=True)

    os.makedirs("output", exist_ok=True)
    with open("output/candidates.md", "w") as f:
        f.write("# US Full-Stack & AI Candidates\n\n")
        for r in results:
            f.write(f"- **{r['login']}** ({r['score']}) — {r['tags']}\n")
            f.write(f"  {r['url']}\n")

if __name__ == "__main__":
    main()
