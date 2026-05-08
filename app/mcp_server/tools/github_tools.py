from typing import Annotated
from mcp.server.fastmcp import FastMCP
from mcp import types as mcp_types

from app.integrations import github_client as gh


def register(mcp: FastMCP, get_app_state) -> None:

    @mcp.tool(description="List public GitHub repositories for a user.")
    async def list_github_repos(
        username: Annotated[str, "GitHub username to list repos for"],
        per_page: Annotated[int, "Number of repos to return (max 100)"] = 30,
    ) -> list[dict]:
        state = get_app_state()
        session = state.get("session")
        token = session.github_token if session else ""
        repos = await gh.list_repos(state["http_client"], token, username, per_page)
        return [
            {
                "name": r["name"],
                "full_name": r["full_name"],
                "description": r.get("description"),
                "url": r["html_url"],
                "stars": r.get("stargazers_count", 0),
                "language": r.get("language"),
            }
            for r in repos
        ]

    @mcp.tool(description="Create a GitHub issue in a repository.")
    async def create_github_issue(
        owner: Annotated[str, "Repository owner (username or org)"],
        repo: Annotated[str, "Repository name"],
        title: Annotated[str, "Issue title"],
        body: Annotated[str, "Issue body/description"] = "",
        labels: Annotated[list[str], "List of label names to apply"] = [],
    ) -> dict:
        state = get_app_state()
        session = state.get("session")
        token = session.github_token if session else ""
        issue = await gh.create_issue(
            state["http_client"], token, owner, repo, title, body, labels
        )
        return {
            "number": issue["number"],
            "title": issue["title"],
            "url": issue["html_url"],
            "state": issue["state"],
        }
