from agents import function_tool, RunContextWrapper
from chatkit.agents import AgentContext

from .db import fetch_products_from_db
from .product_widget import build_product_widget, product_widget_copy_text

# Load product catalog once
PRODUCTS = fetch_products_from_db()


@function_tool(
    description_override=(
        "Show a product card for a specific product.\n"
        "- `product_id`: ID or key of the product to display."
    )
)
async def show_product_card(
    ctx: RunContextWrapper[AgentContext],
    product_id: str,
):
    product = PRODUCTS.get(product_id)

    if not product:
        return {
            "error": f"No product found with id '{product_id}'"
        }

    # Build widget
    widget = build_product_widget(product)
    print(widget.model_dump_json(indent=2))

    # Stream widget to the client
    await ctx.context.stream_widget(
        widget,
        copy_text=product_widget_copy_text(product),
    )

    # Optional: return minimal structured data for agent reasoning
    return {
        "id": product_id,
        "title": product.get("title"),
        "price": product.get("price"),
        "currency": product.get("currency"),
    }
