# """
# ChatKit server with:
# - Intent classification
# - Agent routing
# - Label-based static knowledge retrieval
# - Product catalog search & filtering
# - Token-efficient context injection
# """

# import json
# from agents import Runner, Agent
# from chatkit.agents import (
#     AgentContext,
#     simple_to_agent_input,
#     stream_agent_response,
# )
# from chatkit.server import ChatKitServer
# from chatkit.types import ThreadMetadata, ThreadStreamEvent, UserMessageItem

# from .memory_store import MemoryStore
# from .db import fetch_products_from_db, product_label_context


# # --------------------------------------------------
# # Config
# # --------------------------------------------------

# MAX_RECENT_ITEMS = 30
# MODEL = "gpt-4.1-mini"


# # --------------------------------------------------
# # Static Knowledge Stores
# # --------------------------------------------------

# SUPPORT_KNOWLEDGE = {
#     "returns_policy": {
#         "labels": ["returns", "refunds", "exchanges"],
#         "text": (
#             "siecle allows customers to return unwanted items purchased "
#             "online or in-store, provided they are unused, in their original condition, "
#             "and include all original packaging and labels. Some items may be excluded "
#             "from returns for hygiene or customisation reasons."
#         ),
#     },
#     "refunds_info": {
#         "labels": ["refunds", "returns"],
#         "text": (
#             "Refunds are typically issued to the original payment method once a returned "
#             "item has been received and checked. Processing times may vary depending on "
#             "the payment provider."
#         ),
#     },
#     "delivery_info": {
#         "labels": ["delivery", "shipping"],
#         "text": (
#             "siecle offers multiple delivery options depending on location and "
#             "order size. Delivery costs and estimated times are shown during checkout."
#         ),
#     },
#     "order_tracking": {
#         "labels": ["delivery", "tracking", "orders"],
#         "text": (
#             "Once an online order has been dispatched, customers can usually track "
#             "their order using a tracking link provided by email or through their account."
#         ),
#     },
#     "terms_conditions": {
#         "labels": ["terms", "legal", "conditions"],
#         "text": (
#             "siecle’s terms and conditions cover website use, ordering, pricing, "
#             "availability, delivery, and returns. The latest version is always available "
#             "on the siecle website."
#         ),
#     },
#     "job_roles": {
#         "labels": ["jobs", "openings", "recruitment"],
#         "text": (
#             "ask Dave he has an IT job for 1 million available, dave@vitreon.com "
#         ),
#     },
#     "Gift_Wrapping": {
#         "labels": ["gift_wrapping", "gifts"],
#         "text": (
#             "Objects you choose will be nicely wrapped in tissue paper and an organza or cotton pouch. "
#             "If you want a box choose the gift boxes or contact us directly."
#         ),
#     },
# }


# GENERAL_KNOWLEDGE = {
#     "company_overview": {
#         "labels": ["company_info", "about"],
#         "text": (
#             "siecle is a UK-based sports retail company founded in 1982. "
#             "It operates both physical retail stores and an online shopping platform."
#         ),
#     },
#     "brands_and_products": {
#         "labels": ["brands", "products"],
#         "text": (
#             "siecle sells sportswear, footwear, and equipment from major brands "
#             "such as Nike, Adidas, Puma, and Under Armour, alongside its own brands."
#         ),
#     },
#     "store_locations": {
#         "labels": ["stores", "locations"],
#         "text": (
#             "siecle operates hundreds of stores across the UK and Ireland, "
#             "with additional international locations."
#         ),
#     },
#     "online_shopping": {
#         "labels": ["website", "online", "shopping"],
#         "text": (
#             "The siecle website allows customers to browse products, read reviews, "
#             "check availability, and place orders online."
#         ),
#     },
#     "pricing_and_promotions": {
#         "labels": ["prices", "sales", "discounts"],
#         "text": (
#             "siecle is known for competitive pricing and frequent promotions, "
#             "including sales and clearance offers."
#         ),
#     },
#     "owners": {
#         "labels": ["owners", "founders", "history"],
#         "text": (
#             "siecle's founder is Bill gates, the owner is not Mike Ashley it is bill gates"
#         ),
#     },
#     "logo": {
#         "labels": ["logo"],
#         "text": (
#             "The design is bold and has stars and has black streaks through it"
#         ),
#     },
# }

# # Assumes fetch_products_from_db() returns a dict of product dicts
# PRODUCT_KNOWLEDGE = fetch_products_from_db()


# # --------------------------------------------------
# # Agents
# # --------------------------------------------------

# classifier_agent = Agent(
#     model=MODEL,
#     name="Intent Classifier",
#     instructions=(
#         "Classify the user's intent into ONE label:\n"
#         "- customer_support\n"
#         "- product_finder\n"
#         "- general\n\n"
#         "Return ONLY the label."
#     ),
# )

# context_selector_agent = Agent(
#     model=MODEL,
#     name="Context Selector",
#     instructions=(
#         "Select which knowledge labels are relevant.\n\n"
#         "Available labels:\n"
#         "returns, refunds, exchanges, delivery, shipping, tracking, orders,\n"
#         "terms, legal, conditions,\n"
#         "jobs, openings, recruitment,\n"
#         "owners, founders, history,\n"
#         "logo, design,\n"
#         "gift_wrapping, gifts,\n"
#         "company_info, about, brands, products, stores, locations, website,\n"
#         "online, shopping, prices, sales, discounts\n\n"
#         "Return a comma-separated list of labels.\n"
#         "Return 'none' if no reference information is needed."
#     ),
# )

# product_search_agent = Agent(
#     model=MODEL,
#     name="Product Search Extractor",
#     instructions=(
#         "Analyze the user's request and extract search keywords to query the product database.\n"
#         "Extract key terms regarding:\n"
#         "- Product type (e.g., 'bowl', 'cup', 'trivet')\n"
#         "- Material (e.g., 'porcelain', 'raphia')\n"
#         "- Color (e.g., 'blue', 'orange')\n"
#         "- Usage (e.g., 'gift', 'tea')\n\n"
#         "Return a comma-separated list of keywords.\n"
#         "If the user is asking generally about products (e.g., 'what do you sell?'), return 'all'."
#     ),
# )


# # --------------------------------------------------
# # Instructions
# # --------------------------------------------------

# BASE_SUPPORT_INSTRUCTIONS = (
#     "You are a customer support assistant for siecle. "
#     "Answer clearly and concisely using the provided reference information when relevant. "
#     "Only answer questions about siecle."
# )

# BASE_GENERAL_INSTRUCTIONS = (
#     "You answer general questions about siecle. "
#     "Use the provided reference information when relevant. "
#     "Only answer questions about siecle."
# )

# PRODUCT_BASE_INSTRUCTIONS = (
#     "You are a knowledgeable and helpful Shop Assistant for siecle. "
#     "Your goal is to help the user find the perfect product from the catalog provided below.\n\n"
#     "BEHAVIOR GUIDELINES:\n"
#     "1. **Analyze the Request:** If the user knows exactly what they want, provide the details (price, description) immediately.\n"
#     "2. **Ask Clarifying Questions:** If the user's request is vague (e.g., 'I need a gift'), act like a shop assistant. Ask about their budget, preferred colors, materials, or who the item is for.\n"
#     "3. **Make Recommendations:** Based on their answers, recommend specific items from the 'Available Products' list. Explain WHY you are recommending them.\n"
#     "4. **Be Honest:** If no products match their criteria, apologize and suggest the closest alternative or a general category.\n"
#     "5. **Sales Tone:** Be polite, enthusiastic, and helpful. Do not invent products that are not in the list.\n"
#     "6. **Strict Scope:** Only answer questions about siecle products."
# )


# # --------------------------------------------------
# # Helper Functions
# # --------------------------------------------------

# def select_knowledge_blocks(knowledge_store, selected_labels):
#     blocks = []
#     for entry in knowledge_store.values():
#         if any(label in entry["labels"] for label in selected_labels):
#             blocks.append(entry["text"])
#     return blocks


# def build_reference_context(blocks):
#     if not blocks:
#         return ""
#     return (
#         "\n\nReference information (use only if relevant):\n\n"
#         + "\n\n---\n\n".join(blocks)
#     )


# def find_matching_products(keywords_str):
#     """
#     Simple keyword search against PRODUCT_KNOWLEDGE.
#     """
#     if not PRODUCT_KNOWLEDGE:
#         return []

#     keywords = [k.strip().lower() for k in keywords_str.split(",")]
    
#     # If agent returns 'all', generally we might want to return a summary or a few featured items.
#     # For now, let's limit 'all' to top 5 to prevent token overflow, or return everything if small.
#     if "all" in keywords:
#         return list(PRODUCT_KNOWLEDGE.values())[:10] 

#     matches = []
    
#     for product in PRODUCT_KNOWLEDGE.values():
#         # Create a searchable string from relevant fields
#         searchable_text = (
#             f"{product.get('title', '')} "
#             f"{product.get('description', '')} "
#             f"{' '.join(product.get('labels', []))}"
#         ).lower()
        
#         # Check if ANY keyword hits (broad search) or ALL (strict).
#         # Broad search is usually better for a "finder".
#         if any(keyword in searchable_text for keyword in keywords):
#             matches.append(product)
            
#     return matches


# def build_product_context(products):
#     if not products:
#         return "\n\nAvailable Products: [None found matching specific criteria. Ask the user for more details.]"
    
#     context_str = "\n\nAvailable Products:\n"
#     for p in products:
#         context_str += (
#             f"- Name: {p.get('title', 'Unknown')}\n"
#             f"  Price: {p.get('price', '')} {p.get('currency', '')}\n"
#             f"  Description: {p.get('description', '')}\n"
#             f"  Link: {p.get('product_url', '')}\n"
#             "  ---\n"
#         )
#     return context_str





# # --------------------------------------------------
# # Server
# # --------------------------------------------------

# class StarterChatServer(ChatKitServer):
#     """ChatKit server with multi-agent routing, static knowledge, and product search."""

#     def __init__(self):
#         self.store = MemoryStore()
#         super().__init__(self.store)

#     async def respond(self, thread, item, context):
#         # Load conversation
#         items_page = await self.store.load_thread_items(
#             thread.id,
#             after=None,
#             limit=MAX_RECENT_ITEMS,
#             order="desc",
#             context=context,
#         )
#         items = list(reversed(items_page.data))
#         agent_input = await simple_to_agent_input(items)

#         agent_context = AgentContext(
#             thread=thread,
#             store=self.store,
#             request_context=context,
#         )

#         # -----------------------------
#         # 1. Intent classification
#         # -----------------------------

#         intent_result = await Runner.run(
#             classifier_agent,
#             agent_input,
#             context=agent_context,
#         )
#         intent = intent_result.final_output.strip().lower()

#         # -----------------------------
#         # 2. Logic Routing & Agent Build
#         # -----------------------------

#         if intent == "product_finder":
#             # --- Product Finder Logic ---
            
#             # A. Extract keywords
#             search_result = await Runner.run(
#                 product_search_agent,
#                 agent_input,
#                 context=agent_context
#             )
#             keywords = search_result.final_output.strip().lower()

#             # B. Search/Filter DB
#             matching_products = find_matching_products(keywords)
            
#             # C. Build Context
#             product_context_str = build_product_context(matching_products)

#             # D. Build Agent
#             agent = Agent(
#                 model=MODEL,
#                 name="Product Finder Agent",
#                 instructions=PRODUCT_BASE_INSTRUCTIONS + product_context_str,
#             )

#         else:
#             # --- Static Knowledge Logic (Support / General) ---
            
#             label_result = await Runner.run(
#                 context_selector_agent,
#                 agent_input,
#                 context=agent_context,
#             )
#             label_output = label_result.final_output.strip().lower()

#             reference_context = ""
#             if label_output != "none":
#                 selected_labels = [l.strip() for l in label_output.split(",")]

#                 if intent == "customer_support":
#                     blocks = select_knowledge_blocks(SUPPORT_KNOWLEDGE, selected_labels)
#                     base_inst = BASE_SUPPORT_INSTRUCTIONS
#                 else:
#                     blocks = select_knowledge_blocks(GENERAL_KNOWLEDGE, selected_labels)
#                     base_inst = BASE_GENERAL_INSTRUCTIONS

#                 reference_context = build_reference_context(blocks)
#             else:
#                 base_inst = BASE_GENERAL_INSTRUCTIONS

#             agent = Agent(
#                 model=MODEL,
#                 name="Information Agent",
#                 instructions=base_inst + reference_context,
#             )

#         # -----------------------------
#         # 3. Stream final response
#         # -----------------------------

#         result = Runner.run_streamed(
#             agent,
#             agent_input,
#             context=agent_context,
#         )

#         async for event in stream_agent_response(agent_context, result):
#             yield event


"""
ChatKit server with:
- Intent classification
- Agent routing
- Label-based static knowledge retrieval
- Product catalog search & filtering
- Token-efficient context injection
"""

import json
from agents import Runner, Agent
from chatkit.agents import (
    AgentContext,
    simple_to_agent_input,
    stream_agent_response,
)
from chatkit.server import ChatKitServer
from chatkit.types import ThreadMetadata, ThreadStreamEvent, UserMessageItem

from .memory_store import MemoryStore
from .db import fetch_products_from_db, product_label_context

from agents import Agent, StopAtTools
from .product_tools import show_product_card

from typing import AsyncIterator, Any
from chatkit.widgets import WidgetRoot, WidgetTemplate
from chatkit.types import Action, ThreadMetadata, WidgetItem
from pydantic import BaseModel

class OpenUrlEvent(BaseModel):
    type: str
    url: str

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
            "siecle allows customers to return unwanted items purchased "
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
            "siecle offers multiple delivery options depending on location and "
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
            "siecle’s terms and conditions cover website use, ordering, pricing, "
            "availability, delivery, and returns. The latest version is always available "
            "on the siecle website."
        ),
    },
    "job_roles": {
        "labels": ["jobs", "openings", "recruitment"],
        "text": (
            "ask Dave he has an IT job for 1 million available, dave@vitreon.com "
        ),
    },
    "Gift_Wrapping": {
        "labels": ["gift_wrapping", "gifts"],
        "text": (
            "Objects you choose will be nicely wrapped in tissue paper and an organza or cotton pouch. "
            "If you want a box choose the gift boxes or contact us directly."
        ),
    },
}


GENERAL_KNOWLEDGE = {
    "company_overview": {
        "labels": ["company_info", "about"],
        "text": (
            "siecle is a UK-based sports retail company founded in 1982. "
            "It operates both physical retail stores and an online shopping platform."
        ),
    },
    "brands_and_products": {
        "labels": ["brands", "products"],
        "text": (
            "siecle sells sportswear, footwear, and equipment from major brands "
            "such as Nike, Adidas, Puma, and Under Armour, alongside its own brands."
        ),
    },
    "store_locations": {
        "labels": ["stores", "locations"],
        "text": (
            "siecle operates hundreds of stores across the UK and Ireland, "
            "with additional international locations."
        ),
    },
    "online_shopping": {
        "labels": ["website", "online", "shopping"],
        "text": (
            "The siecle website allows customers to browse products, read reviews, "
            "check availability, and place orders online."
        ),
    },
    "pricing_and_promotions": {
        "labels": ["prices", "sales", "discounts"],
        "text": (
            "siecle is known for competitive pricing and frequent promotions, "
            "including sales and clearance offers."
        ),
    },
    "owners": {
        "labels": ["owners", "founders", "history"],
        "text": (
            "siecle's founder is Bill gates, the owner is not Mike Ashley it is bill gates"
        ),
    },
    "logo": {
        "labels": ["logo"],
        "text": (
            "The design is bold and has stars and has black streaks through it"
        ),
    },
}

# Assumes fetch_products_from_db() returns a dict of product dicts
PRODUCT_KNOWLEDGE = fetch_products_from_db()


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
        "owners, founders, history,\n"
        "logo, design,\n"
        "gift_wrapping, gifts,\n"
        "company_info, about, brands, products, stores, locations, website,\n"
        "online, shopping, prices, sales, discounts\n\n"
        "Return a comma-separated list of labels.\n"
        "Return 'none' if no reference information is needed."
    ),
)

#We need the full database and we need to run ai to identify what the labels should be given to each product from the description and title
#then we give them those labels in the view and we 
#create a product finder agent that uses those labels to find products like the agent above
product_search_agent = Agent(
    model=MODEL,
    name="Product Search Extractor",
    instructions=(
        "Analyze the user's request and extract search keywords to query the product database.\n"
        "Extract key terms regarding:\n"
        "- Product type (e.g., 'bowl', 'cup', 'trivet')\n"
        "- Material (e.g., 'porcelain', 'raphia')\n"
        "- Color (e.g., 'blue', 'orange')\n"
        "- Usage (e.g., 'gift', 'tea')\n\n"
        "Return a comma-separated list of keywords.\n"
        "If the user is asking generally about products (e.g., 'what do you sell?'), return 'all'."
    ),
)


# --------------------------------------------------
# Instructions
# --------------------------------------------------

BASE_SUPPORT_INSTRUCTIONS = (
    "You are a customer support assistant for siecle. "
    "Answer clearly and concisely using the provided reference information when relevant. "
    "Only answer questions about siecle."
)

BASE_GENERAL_INSTRUCTIONS = (
    "You answer general questions about siecle. "
    "Use the provided reference information when relevant. "
    "Only answer questions about siecle."
)

# PRODUCT_BASE_INSTRUCTIONS = (
#     "You are a knowledgeable and helpful Shop Assistant for siecle. "
#     "Your goal is to help the user find the perfect product from the catalog provided below.\n\n"
#     "BEHAVIOR GUIDELINES:\n"
#     "1. **Analyze the Request:** If the user knows exactly what they want, provide the details (price, description) immediately.\n"
#     "2. **Ask Clarifying Questions:** If the user's request is vague (e.g., 'I need a gift'), act like a shop assistant. Ask about their budget, preferred colors, materials, or who the item is for.\n"
#     "3. **Make Recommendations:** Based on their answers, recommend specific items from the 'Available Products' list. Explain WHY you are recommending them.\n"
#     "4. **Be Honest:** If no products match their criteria, apologize and suggest the closest alternative or a general category.\n"
#     "5. **Sales Tone:** Be polite, enthusiastic, and helpful. Do not invent products that are not in the list.\n"
#     "6. **Strict Scope:** Only answer questions about siecle products."
# )

PRODUCT_AGENT_INSTRUCTIONS = """
You are a Shop Assistant for siecle.

You are given a product catalog with explicit product_id values.

RULES:
- When recommending a specific product, you MUST call `show_product_card`
- You MUST use the EXACT product_id shown in the catalog
- NEVER guess or invent product IDs
- If no suitable product exists, say so clearly
- Maximum of 3 product cards per response
"""


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


def find_matching_products(keywords_str):
    if not PRODUCT_KNOWLEDGE:
        return []

    keywords = [k.strip().lower() for k in keywords_str.split(",")]

    if "all" in keywords:
        return list(PRODUCT_KNOWLEDGE.items())[:10]  # (id, product)

    matches = []

    for product_id, product in PRODUCT_KNOWLEDGE.items():
        searchable_text = (
            f"{product.get('title', '')} "
            f"{product.get('description', '')} "
            f"{' '.join(product.get('labels', []))}"
        ).lower()

        if any(keyword in searchable_text for keyword in keywords):
            matches.append((product_id, product))

    return matches


def build_product_context(products):
    if not products:
        return (
            "\n\nAvailable Products:\n"
            "[None found matching criteria. Ask the user for more details.]"
        )

    context_str = "\n\nAvailable Products:\n"
    for product_id, p in products:
        context_str += (
            f"- product_id: {product_id}\n"
            f"  title: {p.get('title')}\n"
            f"  price: {p.get('price')} {p.get('currency')}\n"
            f"  description: {p.get('description')}\n"
            f"  link: {p.get('product_url')}\n"
            
            "  ---\n"
        )
    return context_str

# --------------------------------------------------
# Server
# --------------------------------------------------

class StarterChatServer(ChatKitServer):
    """ChatKit server with multi-agent routing, static knowledge, and product search."""

    def __init__(self):
        self.store = MemoryStore()
        super().__init__(self.store)




    async def respond(self, thread, item, context):
        if thread:
            try:
                items_page = await self.store.load_thread_items(
                    thread.id,
                    after=None,
                    limit=MAX_RECENT_ITEMS,
                    order="desc",
                    context=context,
                )
                items = list(reversed(items_page.data))
                agent_input = await simple_to_agent_input(items)
            except Exception:
                # THREAD NOT FOUND → fallback to empty conversation
                items = []
                agent_input = {"messages": []}
        else:
            # No thread, stateless mode
            items = []
            agent_input = {"messages": []}

        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

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
        # 2. Logic Routing & Agent Build
        # -----------------------------

        if intent == "product_finder":
            # --- Product Finder Logic ---
            
            # A. Extract keywords
            search_result = await Runner.run(
                product_search_agent,
                agent_input,
                context=agent_context
            )
            keywords = search_result.final_output.strip().lower()

            # B. Search/Filter DB
            matching_products = find_matching_products(keywords)
            
            # C. Build Context
            product_context_str = build_product_context(matching_products)

            agent = Agent(
                model=MODEL,
                name="Product Finder Agent",
                instructions=PRODUCT_AGENT_INSTRUCTIONS + product_context_str,
                tools=[show_product_card],
            )


        else:
            # --- Static Knowledge Logic (Support / General) ---
            
            label_result = await Runner.run(
                context_selector_agent,
                agent_input,
                context=agent_context,
            )
            label_output = label_result.final_output.strip().lower()

            reference_context = ""
            if label_output != "none":
                selected_labels = [l.strip() for l in label_output.split(",")]

                if intent == "customer_support":
                    blocks = select_knowledge_blocks(SUPPORT_KNOWLEDGE, selected_labels)
                    base_inst = BASE_SUPPORT_INSTRUCTIONS
                else:
                    blocks = select_knowledge_blocks(GENERAL_KNOWLEDGE, selected_labels)
                    base_inst = BASE_GENERAL_INSTRUCTIONS

                reference_context = build_reference_context(blocks)
            else:
                base_inst = BASE_GENERAL_INSTRUCTIONS

            agent = Agent(
                model=MODEL,
                name="Information Agent",
                instructions=base_inst + reference_context,
            )

        # -----------------------------
        # 3. Stream final response
        # -----------------------------

        result = Runner.run_streamed(
            agent,
            agent_input,
            context=agent_context,
        )

        async for event in stream_agent_response(agent_context, result):
            yield event

   