"""Web scraping agent using AI-powered extraction.

This module provides a Streamlit interface for scraping websites
using OpenAI-powered intelligent extraction with ScrapegraphAI.
"""

import logging
from typing import Optional

import streamlit as st
from scrapegraphai.graphs import SmartScraperGraph

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Configuration
SUPPORTED_MODELS: list[str] = ["gpt-3.5-turbo", "gpt-4"]
DEFAULT_MODEL_INDEX: int = 0


def validate_inputs(api_key: str, url: str, prompt: str) -> bool:
    """Validate user inputs.

    Args:
        api_key (str): OpenAI API key.
        url (str): Website URL.
        prompt (str): Scraping prompt.

    Returns:
        bool: True if inputs are valid.
    """
    if not api_key:
        st.warning("Please enter your OpenAI API key")
        return False
    if not url:
        st.warning("Please enter a website URL")
        return False
    if not prompt:
        st.warning("Please enter what you want to scrape")
        return False
    return True


def scrape_website(
    api_key: str, url: str, prompt: str, model: str
) -> Optional[str]:
    """Scrape website using AI-powered extraction.

    Args:
        api_key (str): OpenAI API key.
        url (str): Website URL.
        prompt (str): Scraping instructions.
        model (str): LLM model to use.

    Returns:
        Optional[str]: Scraped content or None if failed.

    Raises:
        Exception: If scraping fails.
    """
    try:
        graph_config = {
            "llm": {
                "api_key": api_key,
                "model": model,
            },
        }

        scraper = SmartScraperGraph(
            prompt=prompt,
            source=url,
            config=graph_config,
        )

        logger.info(f"Scraping {url} with model {model}")
        result = scraper.run()
        logger.info("Scraping completed successfully")
        return result

    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise


def main() -> None:
    """Main Streamlit application."""
    st.title("Web Scraping AI Agent")
    st.caption("Extract data from websites using OpenAI API")

    # API key input
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Enter your OpenAI API key",
    )

    if not api_key:
        st.info("Enter your API key to begin")
        return

    # Model selection
    model = st.radio(
        "Select Model",
        SUPPORTED_MODELS,
        index=DEFAULT_MODEL_INDEX,
    )

    # URL input
    url = st.text_input(
        "Website URL",
        placeholder="https://example.com",
        help="Enter the website URL to scrape",
    )

    # Prompt input
    prompt = st.text_input(
        "Extraction Instructions",
        placeholder="What do you want to extract from the website?",
        help="Describe what data to extract",
    )

    # Scrape button
    if st.button("Scrape", type="primary"):
        if validate_inputs(api_key, url, prompt):
            try:
                with st.spinner("Scraping website..."):
                    result = scrape_website(api_key, url, prompt, model)
                    st.success("Scraping completed!")
                    st.write("### Results:")
                    st.write(result)
            except Exception as e:
                logger.error(f"Scraping error: {e}")
                st.error(f"Scraping failed: {str(e)}")


if __name__ == "__main__":
    main()