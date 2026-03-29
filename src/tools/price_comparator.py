import json
import statistics
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class PriceComparatorInput(BaseModel):
    product_name: str = Field(description="Name of the product being compared")
    prices: list = Field(
        description=(
            "List of price entries, each a dict with 'source' (seller name) "
            "and 'price' (numeric value). Example: "
            '[{"source": "Amazon", "price": 29.99}, {"source": "eBay", "price": 24.50}]'
        )
    )


class PriceComparatorTool(BaseTool):
    name: str = "price_comparator"
    description: str = (
        "Compare prices across multiple sources for a product. "
        "Calculates min, max, median, mean price and identifies the best deal "
        "with savings percentage. Helps determine if a deal is genuinely good."
    )
    args_schema: Type[BaseModel] = PriceComparatorInput

    def _run(self, product_name: str, prices: list) -> str:
        try:
            valid_prices = []
            for entry in prices:
                if isinstance(entry, dict) and "price" in entry:
                    try:
                        price_val = float(entry["price"])
                        if price_val > 0:
                            valid_prices.append(
                                {
                                    "source": entry.get("source", "Unknown"),
                                    "price": price_val,
                                }
                            )
                    except (ValueError, TypeError):
                        continue

            if not valid_prices:
                return json.dumps(
                    {
                        "success": False,
                        "error": "No valid prices provided",
                    }
                )

            price_values = [p["price"] for p in valid_prices]
            sorted_prices = sorted(valid_prices, key=lambda x: x["price"])

            min_price = min(price_values)
            max_price = max(price_values)
            mean_price = statistics.mean(price_values)
            median_price = statistics.median(price_values)

            best_deal = sorted_prices[0]
            savings_vs_avg = ((mean_price - best_deal["price"]) / mean_price) * 100
            savings_vs_max = ((max_price - best_deal["price"]) / max_price) * 100

            result = {
                "success": True,
                "product_name": product_name,
                "total_sources": len(valid_prices),
                "price_stats": {
                    "min": round(min_price, 2),
                    "max": round(max_price, 2),
                    "mean": round(mean_price, 2),
                    "median": round(median_price, 2),
                    "range": round(max_price - min_price, 2),
                },
                "best_deal": {
                    "source": best_deal["source"],
                    "price": best_deal["price"],
                    "savings_vs_average_pct": round(savings_vs_avg, 1),
                    "savings_vs_highest_pct": round(savings_vs_max, 1),
                },
                "price_ranking": [
                    {
                        "rank": i + 1,
                        "source": p["source"],
                        "price": p["price"],
                        "vs_average": round(
                            ((mean_price - p["price"]) / mean_price) * 100, 1
                        ),
                    }
                    for i, p in enumerate(sorted_prices)
                ],
            }

            return json.dumps(result)

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
