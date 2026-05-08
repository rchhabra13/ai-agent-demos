import os
from datetime import datetime
from typing import Optional, Dict, Any
from neo4j import GraphDatabase


class Neo4jClient:
    def __init__(self):
        uri = os.environ["NEO4J_URI"]
        user = os.environ["NEO4J_USER"]
        password = os.environ["NEO4J_PASSWORD"]
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def ping(self) -> bool:
        try:
            self._driver.verify_connectivity()
            return True
        except Exception:
            return False

    def upsert_company(self, ticker: str, name: str, sector: Optional[str], industry: Optional[str]):
        with self._driver.session() as session:
            session.run(
                """
                MERGE (c:Company {ticker: $ticker})
                SET c.name = $name, c.sector = $sector, c.industry = $industry,
                    c.updated_at = $now
                """,
                ticker=ticker, name=name, sector=sector, industry=industry,
                now=datetime.utcnow().isoformat(),
            )

    def store_metrics(self, ticker: str, financials: Dict[str, Any], period: str):
        """Store key financial metrics as Metric nodes linked to Company."""
        with self._driver.session() as session:
            metric_fields = [
                ("revenue", financials.get("revenue", [None])[0], "USD_millions"),
                ("net_income", financials.get("net_income", [None])[0], "USD_millions"),
                ("operating_cash_flow", financials.get("operating_cash_flow", [None])[0], "USD_millions"),
                ("capex", financials.get("capex", [None])[0], "USD_millions"),
            ]
            for name, value, unit in metric_fields:
                if value is None:
                    continue
                session.run(
                    """
                    MATCH (c:Company {ticker: $ticker})
                    MERGE (m:Metric {company: $ticker, name: $name, period: $period})
                    SET m.value = $value, m.unit = $unit
                    MERGE (c)-[:HAS_METRIC]->(m)
                    """,
                    ticker=ticker, name=name, period=period, value=value, unit=unit,
                )

    def store_analysis(self, ticker: str, recommendation: str, confidence: float, memo_snippet: str):
        with self._driver.session() as session:
            session.run(
                """
                MATCH (c:Company {ticker: $ticker})
                CREATE (a:Analysis {
                    company: $ticker,
                    recommendation: $recommendation,
                    confidence: $confidence,
                    memo_snippet: $memo_snippet,
                    analyzed_at: $now
                })
                MERGE (c)-[:HAS_ANALYSIS]->(a)
                """,
                ticker=ticker, recommendation=recommendation,
                confidence=confidence, memo_snippet=memo_snippet[:500],
                now=datetime.utcnow().isoformat(),
            )

    def get_company_history(self, ticker: str) -> list:
        with self._driver.session() as session:
            result = session.run(
                """
                MATCH (c:Company {ticker: $ticker})-[:HAS_ANALYSIS]->(a:Analysis)
                RETURN a.recommendation AS rec, a.confidence AS conf,
                       a.analyzed_at AS date
                ORDER BY a.analyzed_at DESC LIMIT 10
                """,
                ticker=ticker,
            )
            return [dict(r) for r in result]
