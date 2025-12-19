
"""
ChatKit server with:
- Intent classification
- Agent routing
- Label-based static knowledge retrieval
- Token-efficient context injection
"""

from agents import Runner, Agent
from chatkit.agents import (
    AgentContext,
    simple_to_agent_input,
    stream_agent_response,
)
from chatkit.server import ChatKitServer
from chatkit.types import ThreadMetadata, ThreadStreamEvent, UserMessageItem

from .memory_store import MemoryStore


# --------------------------------------------------
# Config
# --------------------------------------------------

MAX_RECENT_ITEMS = 30
MODEL = "gpt-4.1-mini"


# --------------------------------------------------
# Static Knowledge Stores
# --------------------------------------------------

SUPPORT_KNOWLEDGE = {
    "returns_policy": {
        "labels": ["returns", "refunds", "exchanges"],
        "text": (
            "bollocks inc allows customers to return unwanted items purchased "
            "online or in-store, provided they are unused, in their original condition, "
            "and include all original packaging and labels. Some items may be excluded "
            "from returns for hygiene or customisation reasons."
        ),
    },
    "refunds_info": {
        "labels": ["refunds", "returns"],
        "text": (
            "Refunds are typically issued to the original payment method once a returned "
            "item has been received and checked. Processing times may vary depending on "
            "the payment provider."
        ),
    },
    "delivery_info": {
        "labels": ["delivery", "shipping"],
        "text": (
            "bollocks inc offers multiple delivery options depending on location and "
            "order size. Delivery costs and estimated times are shown during checkout."
        ),
    },
    "order_tracking": {
        "labels": ["delivery", "tracking", "orders"],
        "text": (
            "Once an online order has been dispatched, customers can usually track "
            "their order using a tracking link provided by email or through their account."
        ),
    },
    "terms_conditions": {
        "labels": ["terms", "legal", "conditions"],
        "text": (
            "bollocks inc’s terms and conditions cover website use, ordering, pricing, "
            "availability, delivery, and returns. The latest version is always available "
            "on the bollocks inc website."
        ),
    },
    "job_roles": {
        "labels": ["jobs", "openings", "recruitment"],
        "text": (
            "ask Dave he has an IT job for 1 million available, dave@vitreon.com "
            
        ),
    },

}


GENERAL_KNOWLEDGE = {
    "company_overview": {
        "labels": ["company_info", "about"],
        "text": (
            "bollocks inc is a UK-based sports retail company founded in 1982. "
            "It operates both physical retail stores and an online shopping platform."
        ),
    },
    "brands_and_products": {
        "labels": ["brands", "products"],
        "text": (
            "bollocks inc sells sportswear, footwear, and equipment from major brands "
            "such as Nike, Adidas, Puma, and Under Armour, alongside its own brands."
        ),
    },
    "store_locations": {
        "labels": ["stores", "locations"],
        "text": (
            "bollocks inc operates hundreds of stores across the UK and Ireland, "
            "with additional international locations."
        ),
    },
    "online_shopping": {
        "labels": ["website", "online", "shopping"],
        "text": (
            "The bollocks inc website allows customers to browse products, read reviews, "
            "check availability, and place orders online."
        ),
    },
    "pricing_and_promotions": {
        "labels": ["prices", "sales", "discounts"],
        "text": (
            "bollocks inc is known for competitive pricing and frequent promotions, "
            "including sales and clearance offers."
        ),
    },
    "owners": {
        "labels": ["owners", "founders", "history"],
        "text": (
            "bollocks inc was founder is Bill gates, the owner is not Mike Ashley it is bill gates"
        ),
    }
}


# --------------------------------------------------
# Agents
# --------------------------------------------------

classifier_agent = Agent(
    model=MODEL,
    name="Intent Classifier",
    instructions=(
        "Classify the user's intent into ONE label:\n"
        "- customer_support\n"
        "- product_finder\n"
        "- general\n\n"
        "Return ONLY the label."
    ),
)

context_selector_agent = Agent(
    model=MODEL,
    name="Context Selector",
    instructions=(
        "Select which knowledge labels are relevant.\n\n"
        "Available labels:\n"
        "returns, refunds, exchanges, delivery, shipping, tracking, orders,\n"
        "terms, legal, conditions,\n"
        "jobs, openings, recruitment,\n"
        "owners, founders, history,\n" \
        "company_info, about, brands, products, stores, locations, website,\n"
        "online, shopping, prices, sales, discounts\n\n"
        "Return a comma-separated list of labels.\n"
        "Return 'none' if no reference information is needed."
    ),
)

BASE_SUPPORT_INSTRUCTIONS = (
    "You are a customer support assistant for a bollocks inc"
    "Answer clearly and concisely using the provided reference information when relevant."
)

BASE_GENERAL_INSTRUCTIONS = (
    "You answer general questions about ew business"
    "Use the provided reference information when relevant."
)

product_finder_agent = Agent(
    model=MODEL,
    name="Product Finder Agent",
    instructions=(
        "You help users find and compare bollocks inc products. "
        "Recommend relevant products and explain why."
    ),
)


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def select_knowledge_blocks(knowledge_store, selected_labels):
    blocks = []
    for entry in knowledge_store.values():
        if any(label in entry["labels"] for label in selected_labels):
            blocks.append(entry["text"])
    return blocks


def build_reference_context(blocks):
    if not blocks:
        return ""
    return (
        "\n\nReference information (use only if relevant):\n\n"
        + "\n\n---\n\n".join(blocks)
    )


# --------------------------------------------------
# Server
# --------------------------------------------------

class StarterChatServer(ChatKitServer):
    """ChatKit server with multi-agent routing and static knowledge injection."""

    def __init__(self):
        self.store = MemoryStore()
        super().__init__(self.store)

    async def respond(self, thread, item, context):
        # Load conversation
        items_page = await self.store.load_thread_items(
            thread.id,
            after=None,
            limit=MAX_RECENT_ITEMS,
            order="desc",
            context=context,
        )
        items = list(reversed(items_page.data))
        agent_input = await simple_to_agent_input(items)

        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

        # -----------------------------
        # 1. Intent classification
        # -----------------------------

        intent_result = await Runner.run(
            classifier_agent,
            agent_input,
            context=agent_context,
        )
        intent = intent_result.final_output.strip().lower()

        # -----------------------------
        # 2. Optional context selection
        # -----------------------------

        reference_context = ""

        if intent in ("customer_support", "general"):
            label_result = await Runner.run(
                context_selector_agent,
                agent_input,
                context=agent_context,
            )
            label_output = label_result.final_output.strip().lower()

            if label_output != "none":
                selected_labels = [l.strip() for l in label_output.split(",")]

                if intent == "customer_support":
                    blocks = select_knowledge_blocks(
                        SUPPORT_KNOWLEDGE, selected_labels
                    )
                else:
                    blocks = select_knowledge_blocks(
                        GENERAL_KNOWLEDGE, selected_labels
                    )

                reference_context = build_reference_context(blocks)

        # -----------------------------
        # 3. Build final agent
        # -----------------------------

        if intent == "customer_support":
            agent = Agent(
                model=MODEL,
                name="Customer Support Agent",
                instructions=BASE_SUPPORT_INSTRUCTIONS + reference_context,
            )
        elif intent == "general":
            agent = Agent(
                model=MODEL,
                name="General Agent",
                instructions=BASE_GENERAL_INSTRUCTIONS + reference_context,
            )
        else:
            agent = product_finder_agent

        # -----------------------------
        # 4. Stream final response
        # -----------------------------

        result = Runner.run_streamed(
            agent,
            agent_input,
            context=agent_context,
        )

        async for event in stream_agent_response(agent_context, result):
            yield event
