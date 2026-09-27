import pytest
import respx
import httpx

from app.integrations.github_client import list_repos, create_issue


@pytest.mark.asyncio
async def test_list_repos():
    with respx.mock:
        respx.get("https://api.github.com/users/octocat/repos").mock(
            return_value=httpx.Response(200, json=[
                {
                    "name": "hello-world",
                    "full_name": "octocat/hello-world",
                    "description": "My first repo",
                    "html_url": "https://github.com/octocat/hello-world",
                    "stargazers_count": 1842,
                    "language": "Python",
                }
            ])
        )
        async with httpx.AsyncClient() as client:
            repos = await list_repos(client, "fake_token", "octocat")
        assert len(repos) == 1
        assert repos[0]["name"] == "hello-world"
        assert repos[0]["stargazers_count"] == 1842


@pytest.mark.asyncio
async def test_create_issue():
    with respx.mock:
        respx.post("https://api.github.com/repos/octocat/hello-world/issues").mock(
            return_value=httpx.Response(201, json={
                "number": 42,
                "title": "Found a bug",
                "html_url": "https://github.com/octocat/hello-world/issues/42",
                "state": "open",
                "body": "Something broke",
            })
        )
        async with httpx.AsyncClient() as client:
            issue = await create_issue(
                client, "fake_token", "octocat", "hello-world",
                "Found a bug", "Something broke", []
            )
        assert issue["number"] == 42
        assert issue["state"] == "open"


@pytest.mark.asyncio
async def test_list_repos_404():
    with respx.mock:
        respx.get("https://api.github.com/users/nobody/repos").mock(
            return_value=httpx.Response(404, json={"message": "Not Found"})
        )
        async with httpx.AsyncClient() as client:
            with pytest.raises(httpx.HTTPStatusError):
                await list_repos(client, "fake_token", "nobody")
