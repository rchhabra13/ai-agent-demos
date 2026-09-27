import httpx

GITHUB_API = "https://api.github.com"


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}


async def list_repos(client: httpx.AsyncClient, token: str, username: str, per_page: int = 30) -> list[dict]:
    resp = await client.get(
        f"{GITHUB_API}/users/{username}/repos",
        headers=_auth_headers(token),
        params={"per_page": per_page, "sort": "updated"},
    )
    resp.raise_for_status()
    return resp.json()


async def create_issue(
    client: httpx.AsyncClient,
    token: str,
    owner: str,
    repo: str,
    title: str,
    body: str,
    labels: list[str],
) -> dict:
    resp = await client.post(
        f"{GITHUB_API}/repos/{owner}/{repo}/issues",
        headers=_auth_headers(token),
        json={"title": title, "body": body, "labels": labels},
    )
    resp.raise_for_status()
    return resp.json()
