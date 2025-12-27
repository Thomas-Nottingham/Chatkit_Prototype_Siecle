"""FastAPI entrypoint for the ChatKit starter backend."""

from __future__ import annotations

from chatkit.server import StreamingResult
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse

from .server import StarterChatServer
from dotenv import load_dotenv
import os
from .db import fetch_products_from_db, product_label_context

load_dotenv()  # loads .env file
print("OPENAI_API_KEY =", os.environ.get("OPENAI_API_KEY"))
app = FastAPI(title="ChatKit Starter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chatkit_server = StarterChatServer()


@app.post("/chatkit")
async def chatkit_endpoint(request: Request) -> Response:
    """Proxy the ChatKit web component payload to the server implementation."""
    payload = await request.body()
    result = await chatkit_server.process(payload, {"request": request})

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    if hasattr(result, "json"):
        return Response(content=result.json, media_type="application/json")
    return JSONResponse(result)

@app.get("/products")
async def get_products(category: str | None = None):
    products = fetch_products_from_db(category_filter=category)
    context = product_label_context()
    
    
    # Print to console (VS Code terminal) for debugging
    print("Products fetched from DB:")
    print(products)

     
    print(context)
    
    return products

# @app.get("/products")
# async def get_product_labels(category: str | None = None):
    
#     # Print to console (VS Code terminal) for debugging
#     print("Products labels from DB:")
   
    
#     return context