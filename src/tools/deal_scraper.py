import json
import re
from typing import Type

import requests
from bs4 import BeautifulSoup
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DealScraperInput(BaseModel):
    url: str = Field(description="URL of the product listing page to scrape")
    extract_phone: bool = Field(
        default=True, description="Whether to look for phone numbers on the page"
    )
    extract_price: bool = Field(
        default=True, description="Whether to look for prices on the page"
    )


class DealScraperTool(BaseTool):
    name: str = "deal_scraper"
    description: str = (
        "Scrape a product listing page to extract deal details: "
        "price, description, seller info, phone number, shipping, and availability. "
        "Works best on standard e-commerce pages."
    )
    args_schema: Type[BaseModel] = DealScraperInput

    def _run(
        self,
        url: str,
        extract_phone: bool = True,
        extract_price: bool = True,
    ) -> str:
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            result = {
                "url": url,
                "title": self._extract_title(soup),
                "description": self._extract_description(soup),
                "price": self._extract_price(soup, resp.text) if extract_price else None,
                "phone": self._extract_phone(resp.text) if extract_phone else None,
                "seller": self._extract_seller(soup),
                "shipping_info": self._extract_shipping(soup, resp.text),
                "in_stock": self._check_availability(soup, resp.text),
            }

            return json.dumps({"success": True, **result})

        except Exception as e:
            return json.dumps({"success": False, "url": url, "error": str(e)})

    def _extract_title(self, soup: BeautifulSoup) -> str:
        # Try og:title first, then <title>, then h1
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"].strip()

        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            return title_tag.string.strip()

        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)

        return "Unknown"

    def _extract_description(self, soup: BeautifulSoup) -> str:
        # Try og:description, then meta description, then first paragraph
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            return og_desc["content"].strip()[:500]

        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"].strip()[:500]

        # Try schema.org product description
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                import json as _json
                data = _json.loads(script.string or "")
                if isinstance(data, dict) and data.get("description"):
                    return str(data["description"])[:500]
            except (ValueError, TypeError):
                pass

        first_p = soup.find("p")
        if first_p:
            return first_p.get_text(strip=True)[:500]

        return "No description available"

    def _extract_price(self, soup: BeautifulSoup, html: str) -> str | None:
        # Try schema.org price
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                import json as _json
                data = _json.loads(script.string or "")
                if isinstance(data, dict):
                    offers = data.get("offers", data)
                    if isinstance(offers, list):
                        offers = offers[0] if offers else {}
                    price = offers.get("price") or offers.get("lowPrice")
                    if price:
                        return str(price)
            except (ValueError, TypeError, IndexError):
                pass

        # Try common price patterns in HTML
        price_patterns = [
            r'₪[\d,]+\.?\d*',
            r'ILS\s*[\d,]+\.?\d*',
            r'\$[\d,]+\.?\d*',
            r'USD\s*[\d,]+\.?\d*',
            r'price["\s:]*[₪$]?([\d,]+\.?\d*)',
        ]
        for pattern in price_patterns:
            match = re.search(pattern, html)
            if match:
                return match.group(0).replace("$", "").replace("₪", "").replace(",", "").strip()

        return None

    def _extract_phone(self, html: str) -> str | None:
        phone_patterns = [
            r'\+972[-.\s]?\d{1,2}[-.\s]?\d{3}[-.\s]?\d{4}',  # Israeli +972
            r'0[2-9]\d?[-.\s]?\d{3}[-.\s]?\d{4}',  # Israeli local
            r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        ]
        for pattern in phone_patterns:
            match = re.search(pattern, html)
            if match:
                return match.group(0).strip()
        return "N/A"

    def _extract_seller(self, soup: BeautifulSoup) -> str:
        # Try og:site_name
        og_site = soup.find("meta", property="og:site_name")
        if og_site and og_site.get("content"):
            return og_site["content"].strip()

        # Try schema.org seller
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                import json as _json
                data = _json.loads(script.string or "")
                if isinstance(data, dict):
                    seller = data.get("seller", {})
                    if isinstance(seller, dict) and seller.get("name"):
                        return seller["name"]
            except (ValueError, TypeError):
                pass

        return "Unknown"

    def _extract_shipping(self, soup: BeautifulSoup, html: str) -> str:
        shipping_keywords = ["free shipping", "free delivery", "ships free"]
        html_lower = html.lower()
        for keyword in shipping_keywords:
            if keyword in html_lower:
                return "Free shipping"

        shipping_match = re.search(
            r'shipping[:\s]*\$?([\d.]+)', html_lower
        )
        if shipping_match:
            return f"${shipping_match.group(1)}"

        return "unknown"

    def _check_availability(self, soup: BeautifulSoup, html: str) -> bool:
        html_lower = html.lower()
        out_of_stock_phrases = ["out of stock", "sold out", "unavailable", "currently unavailable"]
        for phrase in out_of_stock_phrases:
            if phrase in html_lower:
                return False
        return True
