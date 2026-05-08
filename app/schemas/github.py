from pydantic import BaseModel


class Repo(BaseModel):
    name: str
    full_name: str
    description: str | None = None
    html_url: str
    stargazers_count: int = 0
    language: str | None = None
    private: bool = False


class Issue(BaseModel):
    number: int
    title: str
    html_url: str
    state: str
    body: str | None = None


class CreateIssueRequest(BaseModel):
    owner: str
    repo: str
    title: str
    body: str = ""
    labels: list[str] = []
