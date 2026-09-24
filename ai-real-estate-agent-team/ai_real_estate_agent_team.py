"""
AI Real Estate Agent Team powered by Firecrawl and Google Gemini.

This module implements a multi-agent real estate search and analysis system
that uses Firecrawl for property extraction and AI agents for analysis.
"""

import json
import logging
import os
import re
import time
from typing import Any, Dict, List, Optional

import streamlit as st
from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

DEFAULT_GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
DEFAULT_FIRECRAWL_API_KEY: str = os.getenv("FIRECRAWL_API_KEY", "")


class PropertyDetails(BaseModel):
    """Property listing details."""

    address: str = Field(description="Full property address")
    price: Optional[str] = Field(description="Property price")
    bedrooms: Optional[str] = Field(description="Number of bedrooms")
    bathrooms: Optional[str] = Field(description="Number of bathrooms")
    square_feet: Optional[str] = Field(description="Square footage")
    property_type: Optional[str] = Field(description="Type of property")
    description: Optional[str] = Field(description="Property description")
    features: Optional[List[str]] = Field(description="Property features")
    images: Optional[List[str]] = Field(description="Property image URLs")
    agent_contact: Optional[str] = Field(description="Agent contact information")
    listing_url: Optional[str] = Field(description="Original listing URL")


class PropertyListing(BaseModel):
    """Collection of property listings."""

    properties: List[PropertyDetails] = Field(description="List of properties found")
    total_count: int = Field(description="Total number of properties found")
    source_website: str = Field(description="Website where properties were found")


class DirectFirecrawlAgent:
    """Agent with direct Firecrawl integration for property search."""

    def __init__(
        self,
        firecrawl_api_key: str,
        google_api_key: str,
        model_id: str = "gemini-2.5-flash"
    ) -> None:
        """
        Initialize the DirectFirecrawlAgent.

        Args:
            firecrawl_api_key: Firecrawl API key
            google_api_key: Google API key
            model_id: Google Gemini model ID
        """
        self.agent = Agent(
            model=Gemini(id=model_id, api_key=google_api_key),
            markdown=True,
            description=(
                "I am a real estate expert who helps find and analyze properties "
                "based on user preferences."
            )
        )
        self.firecrawl = FirecrawlApp(api_key=firecrawl_api_key)

    def find_properties_direct(
        self,
        city: str,
        state: str,
        user_criteria: Dict[str, Any],
        selected_websites: List[str]
    ) -> Dict[str, Any]:
        """
        Search for properties using direct Firecrawl integration.

        Args:
            city: City name
            state: State name
            user_criteria: User search criteria
            selected_websites: List of websites to search

        Returns:
            Dictionary containing property data or error message
        """
        city_formatted = city.replace(" ", "-").lower()
        state_upper = state.upper() if state else ""
        state_lower = state.lower() if state else ""
        city_trulia = city.replace(" ", "_")

        search_urls = {
            "Zillow": f"https://www.zillow.com/homes/for_sale/{city_formatted}-{state_upper}/",
            "Realtor.com": f"https://www.realtor.com/realestateandhomes-search/{city_formatted}_{state_upper}/pg-1",
            "Trulia": f"https://www.trulia.com/{state_upper}/{city_trulia}/",
            "Homes.com": f"https://www.homes.com/homes-for-sale/{city_formatted}-{state_lower}/"
        }

        urls_to_search = [
            url for site, url in search_urls.items()
            if site in selected_websites
        ]

        logger.info(f"Selected websites: {selected_websites}")
        logger.info(f"URLs to search: {urls_to_search}")

        if not urls_to_search:
            return {"error": "No websites selected"}

        prompt = f"""You are extracting property listings from real estate websites. Extract EVERY property listing you can find on the page.

USER SEARCH CRITERIA:
- Budget: {user_criteria.get('budget_range', 'Any')}
- Property Type: {user_criteria.get('property_type', 'Any')}
- Bedrooms: {user_criteria.get('bedrooms', 'Any')}
- Bathrooms: {user_criteria.get('bathrooms', 'Any')}
- Min Square Feet: {user_criteria.get('min_sqft', 'Any')}
- Special Features: {user_criteria.get('special_features', 'Any')}

EXTRACTION INSTRUCTIONS:
1. Find ALL property listings on the page (usually 20-40 per page)
2. For EACH property, extract these fields:
   - address: Full street address (required)
   - price: Listed price with $ symbol (required)
   - bedrooms: Number of bedrooms (required)
   - bathrooms: Number of bathrooms (required)
   - square_feet: Square footage if available
   - property_type: House/Condo/Townhouse/Apartment etc.
   - description: Brief property description if available
   - listing_url: Direct link to property details if available
   - agent_contact: Agent name/phone if visible

3. CRITICAL REQUIREMENTS:
   - Extract AT LEAST 10 properties if they exist on the page
   - Do NOT skip properties even if some fields are missing
   - Use "Not specified" for missing optional fields
   - Ensure address and price are always filled
   - Look for property cards, listings, search results

4. RETURN FORMAT:
   - Return JSON with "properties" array containing all extracted properties
   - Each property should be a complete object with all available fields
   - Set "total_count" to the number of properties extracted
   - Set "source_website" to the main website name (Zillow/Realtor/Trulia/Homes)

EXTRACT EVERY VISIBLE PROPERTY LISTING - DO NOT LIMIT TO JUST A FEW!
        """

        try:
            logger.info(f"Calling Firecrawl with {len(urls_to_search)} URLs")
            raw_response = self.firecrawl.extract(
                urls_to_search,
                prompt=prompt,
                schema=PropertyListing.model_json_schema()
            )

            logger.info(f"Raw Firecrawl Response: {raw_response}")

            if hasattr(raw_response, "success") and raw_response.success:
                properties = (
                    raw_response.data.get("properties", [])
                    if hasattr(raw_response, "data") else []
                )
                total_count = (
                    raw_response.data.get("total_count", 0)
                    if hasattr(raw_response, "data") else 0
                )
            elif isinstance(raw_response, dict) and raw_response.get("success"):
                properties = raw_response["data"].get("properties", [])
                total_count = raw_response["data"].get("total_count", 0)
            else:
                properties = []
                total_count = 0

            logger.info(
                f"Extracted {len(properties)} properties from {total_count} total found"
            )

            if properties:
                if properties:
                    logger.info(f"First property sample: {properties[0]}")
                return {
                    "success": True,
                    "properties": properties,
                    "total_count": len(properties),
                    "source_websites": selected_websites
                }
            else:
                error_msg = f"""No properties extracted despite finding {total_count} listings.

POSSIBLE CAUSES:
1. Website structure changed - extraction schema doesn't match
2. Website blocking or requiring interaction (captcha, login)
3. Properties don't match specified criteria too strictly
4. Extraction prompt needs refinement for this website

SUGGESTIONS:
- Try different websites (Zillow, Realtor.com, Trulia, Homes.com)
- Broaden search criteria (Any bedrooms, Any type, etc.)
- Check if website requires specific user interaction

Debug Info: Found {total_count} listings but extraction returned empty array."""

                return {"error": error_msg}

        except Exception as e:
            logger.error(f"Firecrawl extraction failed: {str(e)}")
            return {"error": f"Firecrawl extraction failed: {str(e)}"}


def create_sequential_agents(llm: Any, user_criteria: Dict[str, Any]) -> tuple[Agent, Agent, Agent]:
    """
    Create agents for sequential manual execution.

    Args:
        llm: Language model instance
        user_criteria: User search criteria

    Returns:
        tuple: (property_search_agent, market_analysis_agent, property_valuation_agent)
    """
    property_search_agent = Agent(
        name="Property Search Agent",
        model=llm,
        instructions="""
        You are a property search expert. Your role is to find and extract property listings.

        WORKFLOW:
        1. SEARCH FOR PROPERTIES:
           - Use the provided Firecrawl data to extract property listings
           - Focus on properties matching user criteria
           - Extract detailed property information

        2. EXTRACT PROPERTY DATA:
           - Address, price, bedrooms, bathrooms, square footage
           - Property type, features, listing URLs
           - Agent contact information

        3. PROVIDE STRUCTURED OUTPUT:
           - List properties with complete details
           - Include all listing URLs
           - Rank by match quality to user criteria

        IMPORTANT:
        - Focus ONLY on finding and extracting property data
        - Do NOT provide market analysis or valuations
        - Your output will be used by other agents for analysis
        """,
    )

    market_analysis_agent = Agent(
        name="Market Analysis Agent",
        model=llm,
        instructions="""
        You are a market analysis expert. Provide CONCISE market insights.

        REQUIREMENTS:
        - Keep analysis brief and to the point
        - Focus on key market trends only
        - Provide 2-3 bullet points per area
        - Avoid repetition and lengthy explanations

        COVER:
        1. Market Condition: Buyer's/seller's market, price trends
        2. Key Neighborhoods: Brief overview of areas where properties are located
        3. Investment Outlook: 2-3 key points about investment potential

        FORMAT: Use bullet points and keep each section under 100 words.
        """,
    )

    property_valuation_agent = Agent(
        name="Property Valuation Agent",
        model=llm,
        instructions="""
        You are a property valuation expert. Provide CONCISE property assessments.

        REQUIREMENTS:
        - Keep each property assessment brief (2-3 sentences max)
        - Focus on key points only: value, investment potential, recommendation
        - Avoid lengthy analysis and repetition
        - Use bullet points for clarity

        FOR EACH PROPERTY, PROVIDE:
        1. Value: Fair price/Over priced/Under priced - brief reason
        2. Investment Potential: High/Medium/Low - brief reason
        3. Recommendation: One actionable insight

        FORMAT:
        - Use bullet points
        - Keep each property under 50 words
        - Focus on actionable insights only
        """,
    )

    return property_search_agent, market_analysis_agent, property_valuation_agent


def run_sequential_analysis(
    city: str,
    state: str,
    user_criteria: Dict[str, Any],
    selected_websites: List[str],
    firecrawl_api_key: str,
    google_api_key: str,
    update_callback: Any
) -> str | Dict[str, Any]:
    """
    Run agents sequentially with manual coordination.

    Args:
        city: City name
        state: State name
        user_criteria: User search criteria
        selected_websites: Selected websites to search
        firecrawl_api_key: Firecrawl API key
        google_api_key: Google API key
        update_callback: Callback function for progress updates

    Returns:
        Analysis results
    """
    llm = Gemini(id="gemini-2.5-flash", api_key=google_api_key)
    property_search_agent, market_analysis_agent, property_valuation_agent = \
        create_sequential_agents(llm, user_criteria)

    update_callback(0.2, "Searching properties...", "🔍 Property Search Agent: Finding properties...")

    direct_agent = DirectFirecrawlAgent(
        firecrawl_api_key=firecrawl_api_key,
        google_api_key=google_api_key,
        model_id="gemini-2.5-flash"
    )

    properties_data = direct_agent.find_properties_direct(
        city=city,
        state=state,
        user_criteria=user_criteria,
        selected_websites=selected_websites
    )

    if "error" in properties_data:
        return f"Error in property search: {properties_data['error']}"

    properties = properties_data.get("properties", [])
    if not properties:
        return "No properties found matching your criteria."

    update_callback(0.4, "Properties found", f"✅ Found {len(properties)} properties")

    update_callback(0.5, "Analyzing market...", "📊 Market Analysis Agent: Analyzing market trends...")

    market_analysis_prompt = f"""
    Provide CONCISE market analysis for these properties:

    PROPERTIES: {len(properties)} properties in {city}, {state}
    BUDGET: {user_criteria.get('budget_range', 'Any')}

    Give BRIEF insights on:
    • Market condition (buyer's/seller's market)
    • Key neighborhoods where properties are located
    • Investment outlook (2-3 bullet points max)

    Keep each section under 100 words. Use bullet points.
    """

    market_result = market_analysis_agent.run(market_analysis_prompt)
    market_analysis = market_result.content

    update_callback(0.7, "Market analysis complete", "✅ Market analysis completed")

    update_callback(0.8, "Evaluating properties...", "💰 Property Valuation Agent: Evaluating properties...")

    properties_for_valuation = []
    for i, prop in enumerate(properties, 1):
        if isinstance(prop, dict):
            prop_data = {
                "number": i,
                "address": prop.get("address", "Address not available"),
                "price": prop.get("price", "Price not available"),
                "property_type": prop.get("property_type", "Type not available"),
                "bedrooms": prop.get("bedrooms", "Not specified"),
                "bathrooms": prop.get("bathrooms", "Not specified"),
                "square_feet": prop.get("square_feet", "Not specified")
            }
        else:
            prop_data = {
                "number": i,
                "address": getattr(prop, "address", "Address not available"),
                "price": getattr(prop, "price", "Price not available"),
                "property_type": getattr(prop, "property_type", "Type not available"),
                "bedrooms": getattr(prop, "bedrooms", "Not specified"),
                "bathrooms": getattr(prop, "bathrooms", "Not specified"),
                "square_feet": getattr(prop, "square_feet", "Not specified")
            }
        properties_for_valuation.append(prop_data)

    valuation_prompt = f"""
    Provide CONCISE property assessments for each property. Use the EXACT format shown below:

    USER BUDGET: {user_criteria.get('budget_range', 'Any')}

    PROPERTIES TO EVALUATE:
    {json.dumps(properties_for_valuation, indent=2)}

    For EACH property, provide assessment in this EXACT format:

    **Property [NUMBER]: [ADDRESS]**
    • Value: [Fair price/Over priced/Under priced] - [brief reason]
    • Investment Potential: [High/Medium/Low] - [brief reason]
    • Recommendation: [One actionable insight]

    REQUIREMENTS:
    - Start each assessment with "**Property [NUMBER]:**"
    - Keep each property assessment under 50 words
    - Analyze ALL {len(properties)} properties individually
    - Use bullet points as shown
    """

    valuation_result = property_valuation_agent.run(valuation_prompt)
    property_valuations = valuation_result.content

    update_callback(0.9, "Valuation complete", "✅ Property valuations completed")

    update_callback(0.95, "Synthesizing results...", "🤖 Synthesizing final recommendations...")

    logger.info(f"Properties type: {type(properties)}")
    logger.info(f"Properties length: {len(properties)}")

    properties_display = ""
    for i, prop in enumerate(properties, 1):
        if isinstance(prop, dict):
            address = prop.get("address", "Address not available")
            price = prop.get("price", "Price not available")
            prop_type = prop.get("property_type", "Type not available")
            bedrooms = prop.get("bedrooms", "Not specified")
            bathrooms = prop.get("bathrooms", "Not specified")
            square_feet = prop.get("square_feet", "Not specified")
            agent_contact = prop.get("agent_contact", "Contact not available")
            description = prop.get("description", "No description available")
            listing_url = prop.get("listing_url", "#")
        else:
            address = getattr(prop, "address", "Address not available")
            price = getattr(prop, "price", "Price not available")
            prop_type = getattr(prop, "property_type", "Type not available")
            bedrooms = getattr(prop, "bedrooms", "Not specified")
            bathrooms = getattr(prop, "bathrooms", "Not specified")
            square_feet = getattr(prop, "square_feet", "Not specified")
            agent_contact = getattr(prop, "agent_contact", "Contact not available")
            description = getattr(prop, "description", "No description available")
            listing_url = getattr(prop, "listing_url", "#")

        properties_display += f"""
### Property {i}: {address}

**Price:** {price}
**Type:** {prop_type}
**Bedrooms:** {bedrooms} | **Bathrooms:** {bathrooms}
**Square Feet:** {square_feet}
**Agent Contact:** {agent_contact}

**Description:** {description}

**Listing URL:** [View Property]({listing_url})

---
"""

    final_synthesis = f"""
# 🏠 Property Listings Found

**Total Properties:** {len(properties)} properties matching your criteria

{properties_display}

---

# 📊 Market Analysis & Investment Insights

{market_analysis}

---

# 💰 Property Valuations & Recommendations

{property_valuations}

---

# 🔗 All Property Links
    """

    all_text = f"{json.dumps(properties, indent=2)} {market_analysis} {property_valuations}"
    urls = re.findall(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        all_text
    )

    if urls:
        final_synthesis += "\n### Available Property Links:\n"
        for i, url in enumerate(set(urls), 1):
            final_synthesis += f"{i}. {url}\n"

    update_callback(1.0, "Analysis complete", "🎉 Complete analysis ready!")

    return {
        "properties": properties,
        "market_analysis": market_analysis,
        "property_valuations": property_valuations,
        "markdown_synthesis": final_synthesis,
        "total_properties": len(properties)
    }


def extract_property_valuation(
    property_valuations: str,
    property_number: int,
    property_address: str
) -> Optional[str]:
    """
    Extract valuation for a specific property.

    Args:
        property_valuations: Full valuation text
        property_number: Property number
        property_address: Property address

    Returns:
        Valuation for specific property or None
    """
    if not property_valuations:
        return None

    sections = property_valuations.split("**Property")

    for section in sections:
        if section.strip().startswith(f"{property_number}:"):
            clean_section = f"**Property{section}".strip()
            clean_section = clean_section.replace("***", "**")
            return clean_section

    all_sections = property_valuations.split("\n\n")
    for section in all_sections:
        if f"Property {property_number}" in section or f"#{property_number}" in section:
            return section

    for section in all_sections:
        if any(
            word in section.lower()
            for word in property_address.lower().split()[:3]
            if len(word) > 2
        ):
            return section

    return f"**Property {property_number} Analysis**\nAnalysis not available. Review general market analysis."


def display_properties_professionally(
    properties: List[Any],
    market_analysis: str,
    property_valuations: str,
    total_properties: int
) -> None:
    """
    Display properties in professional UI using Streamlit.

    Args:
        properties: List of properties
        market_analysis: Market analysis text
        property_valuations: Property valuations text
        total_properties: Total number of properties
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Properties Found", total_properties)

    with col2:
        prices = []
        for p in properties:
            price_str = p.get("price", "") if isinstance(p, dict) else getattr(p, "price", "")
            if price_str and price_str != "Price not available":
                try:
                    price_num = "".join(filter(str.isdigit, str(price_str)))
                    if price_num:
                        prices.append(int(price_num))
                except (ValueError, TypeError):
                    pass
        avg_price = f"${sum(prices) // len(prices):,}" if prices else "N/A"
        st.metric("Average Price", avg_price)

    with col3:
        types = {}
        for p in properties:
            t = p.get("property_type", "Unknown") if isinstance(p, dict) else getattr(p, "property_type", "Unknown")
            types[t] = types.get(t, 0) + 1
        most_common = max(types.items(), key=lambda x: x[1])[0] if types else "N/A"
        st.metric("Most Common Type", most_common)

    tab1, tab2, tab3 = st.tabs(["🏠 Properties", "📊 Market Analysis", "💰 Valuations"])

    with tab1:
        for i, prop in enumerate(properties, 1):
            data = {
                k: prop.get(k, "") if isinstance(prop, dict) else getattr(prop, k, "")
                for k in [
                    "address", "price", "property_type", "bedrooms",
                    "bathrooms", "square_feet", "description", "listing_url"
                ]
            }

            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(f"#{i} 🏠 {data['address']}")
                with col2:
                    st.metric("Price", data["price"])

                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.markdown(f"**Type:** {data['property_type']}")
                    st.markdown(f"**Beds/Baths:** {data['bedrooms']}/{data['bathrooms']}")
                    st.markdown(f"**Area:** {data['square_feet']}")
                with col2:
                    with st.expander("💰 Investment Analysis"):
                        property_valuation = extract_property_valuation(
                            property_valuations, i, data["address"]
                        )
                        if property_valuation:
                            st.markdown(property_valuation)
                        else:
                            st.info("Investment analysis not available")
                with col3:
                    if data["listing_url"] and data["listing_url"] != "#":
                        st.markdown(
                            f'<a href="{data["listing_url"]}" target="_blank" '
                            'style="text-decoration: none; padding: 0.5rem 1rem; '
                            'background-color: #0066cc; color: white; '
                            'border-radius: 6px; font-size: 0.9em; font-weight: 500;">'
                            "Property Link</a>",
                            unsafe_allow_html=True
                        )

                st.divider()

    with tab2:
        st.subheader("📊 Market Analysis")
        if market_analysis:
            for section in market_analysis.split("\n\n"):
                if section.strip():
                    st.markdown(section)
        else:
            st.info("No market analysis available")

    with tab3:
        st.subheader("💰 Investment Analysis")
        if property_valuations:
            for section in property_valuations.split("\n\n"):
                if section.strip():
                    st.markdown(section)
        else:
            st.info("No valuation data available")


def main() -> None:
    """Main application entry point."""
    st.set_page_config(
        page_title="AI Real Estate Agent Team",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🏠 AI Real Estate Agent Team")
    st.caption("Find Your Dream Home with Specialized AI Agents")

    with st.sidebar:
        st.header("⚙️ Configuration")

        with st.expander("🔑 API Keys", expanded=True):
            google_key = st.text_input(
                "Google AI API Key",
                value=DEFAULT_GOOGLE_API_KEY,
                type="password",
                help="Get your API key from https://aistudio.google.com/app/apikey",
                placeholder="AIza..."
            )
            firecrawl_key = st.text_input(
                "Firecrawl API Key",
                value=DEFAULT_FIRECRAWL_API_KEY,
                type="password",
                help="Get your API key from https://firecrawl.dev",
                placeholder="fc_..."
            )

            if google_key:
                os.environ["GOOGLE_API_KEY"] = google_key
            if firecrawl_key:
                os.environ["FIRECRAWL_API_KEY"] = firecrawl_key

        with st.expander("🌐 Search Sources", expanded=True):
            st.markdown("**Select real estate websites to search:**")
            available_websites = ["Zillow", "Realtor.com", "Trulia", "Homes.com"]
            selected_websites = [
                site for site in available_websites
                if st.checkbox(site, value=site in ["Zillow", "Realtor.com"])
            ]

            if selected_websites:
                st.markdown(f"✅ {len(selected_websites)} sources selected")
            else:
                st.markdown("⚠️ Please select at least one website")

        with st.expander("🤖 How It Works", expanded=False):
            st.markdown("**🔍 Property Search Agent**")
            st.markdown("Uses direct Firecrawl integration to find properties")

            st.markdown("**📊 Market Analysis Agent**")
            st.markdown("Analyzes market trends and neighborhood insights")

            st.markdown("**💰 Property Valuation Agent**")
            st.markdown("Evaluates properties and provides investment analysis")

    st.header("Your Property Requirements")
    st.info("Please provide the location, budget, and property details to help us find your ideal home.")

    with st.form("property_preferences"):
        st.markdown("### 📍 Location & Budget")
        col1, col2 = st.columns(2)

        with col1:
            city = st.text_input(
                "🏙️ City",
                placeholder="e.g., San Francisco",
                help="Enter the city where you want to buy property"
            )
            state = st.text_input(
                "🗺️ State/Province (optional)",
                placeholder="e.g., CA",
                help="Enter the state or province (optional)"
            )

        with col2:
            min_price = st.number_input(
                "💰 Minimum Price ($)",
                min_value=0,
                value=500000,
                step=50000,
                help="Your minimum budget for the property"
            )
            max_price = st.number_input(
                "💰 Maximum Price ($)",
                min_value=0,
                value=1500000,
                step=50000,
                help="Your maximum budget for the property"
            )

        st.markdown("### 🏡 Property Details")
        col1, col2, col3 = st.columns(3)

        with col1:
            property_type = st.selectbox(
                "🏠 Property Type",
                ["Any", "House", "Condo", "Townhouse", "Apartment"],
                help="Type of property you're looking for"
            )
            bedrooms = st.selectbox(
                "🛏️ Bedrooms",
                ["Any", "1", "2", "3", "4", "5+"],
                help="Number of bedrooms required"
            )

        with col2:
            bathrooms = st.selectbox(
                "🚿 Bathrooms",
                ["Any", "1", "1.5", "2", "2.5", "3", "3.5", "4+"],
                help="Number of bathrooms required"
            )
            min_sqft = st.number_input(
                "📏 Minimum Square Feet",
                min_value=0,
                value=1000,
                step=100,
                help="Minimum square footage required"
            )

        with col3:
            timeline = st.selectbox(
                "⏰ Timeline",
                ["Flexible", "1-3 months", "3-6 months", "6+ months"],
                help="When do you plan to buy?"
            )
            urgency = st.selectbox(
                "🚨 Urgency",
                ["Not urgent", "Somewhat urgent", "Very urgent"],
                help="How urgent is your purchase?"
            )

        st.markdown("### ✨ Special Features")
        special_features = st.text_area(
            "🎯 Special Features & Requirements",
            placeholder="e.g., Parking, Yard, View, Near public transport, Good schools",
            help="Any specific features or requirements you're looking for"
        )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "🚀 Start Property Analysis",
                type="primary",
                use_container_width=True
            )

    if submitted:
        missing_items = []
        if not google_key:
            missing_items.append("Google AI API Key")
        if not firecrawl_key:
            missing_items.append("Firecrawl API Key")
        if not city:
            missing_items.append("City")
        if not selected_websites:
            missing_items.append("At least one website selection")

        if missing_items:
            st.error(f"Please provide: {', '.join(missing_items)}")
            return

        try:
            user_criteria = {
                "budget_range": f"${min_price:,} - ${max_price:,}",
                "property_type": property_type,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "min_sqft": min_sqft,
                "special_features": special_features if special_features else "None specified"
            }

        except Exception as e:
            st.error(f"Error initializing: {str(e)}")
            logger.error(f"Initialization error: {str(e)}")
            return

        st.markdown("#### Property Analysis in Progress")
        st.info("AI Agents are searching for your perfect home...")

        status_container = st.container()
        with status_container:
            st.markdown("### 📊 Current Activity")
            progress_bar = st.progress(0)
            current_activity = st.empty()

        def update_progress(progress: float, status: str, activity: Optional[str] = None) -> None:
            """Update progress bar and activity."""
            if activity:
                progress_bar.progress(progress)
                current_activity.text(activity)

        try:
            start_time = time.time()
            update_progress(0.1, "Initializing...", "Starting sequential property analysis")

            final_result = run_sequential_analysis(
                city=city,
                state=state,
                user_criteria=user_criteria,
                selected_websites=selected_websites,
                firecrawl_api_key=firecrawl_key,
                google_api_key=google_key,
                update_callback=update_progress
            )

            total_time = time.time() - start_time

            if isinstance(final_result, dict):
                display_properties_professionally(
                    final_result["properties"],
                    final_result["market_analysis"],
                    final_result["property_valuations"],
                    final_result["total_properties"]
                )
            else:
                st.markdown("### 🏠 Comprehensive Real Estate Analysis")
                st.markdown(final_result)

            st.caption(f"Analysis completed in {total_time:.1f}s")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            logger.error(f"Analysis error: {str(e)}")


if __name__ == "__main__":
    main()
