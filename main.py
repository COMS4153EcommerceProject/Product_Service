from __future__ import annotations
import os
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query, status

from models.product import ProductCreate, ProductRead, ProductUpdate
from models.category import CategoryCreate, CategoryRead, CategoryUpdate
from models.inventory import InventoryCreate, InventoryRead, InventoryUpdate

port = int(os.environ.get("FASTAPIPORT", 8000))

# --------------------------------------------------------------------------
# In-memory "databases"
# --------------------------------------------------------------------------
products: Dict[UUID, ProductRead] = {}
categories: Dict[UUID, CategoryRead] = {}
inventories: Dict[UUID, InventoryRead] = {}

app = FastAPI(
    title="Product/Category/Inventory API",
    description="Demo FastAPI app using Pydantic v2 models for an e-commerce Product module.",
    version="0.1.0",
)

# --------------------------------------------------------------------------
# Product endpoints
# --------------------------------------------------------------------------
@app.post("/products", response_model=ProductRead, status_code=201, tags=["Product"])
def create_product(product: ProductCreate):
    product_read = ProductRead(**product.model_dump())
    products[product_read.product_id] = product_read
    return product_read


@app.get("/products", response_model=List[ProductRead], tags=["Product"])
def list_products(
    name: Optional[str] = Query(None),
    category_id: Optional[UUID] = Query(None),
):
    results = list(products.values())
    if name:
        results = [p for p in results if p.name == name]
    if category_id:
        results = [p for p in results if p.category_id == category_id]
    return results


@app.get("/products/{product_id}", response_model=ProductRead, tags=["Product"])
def get_product(product_id: UUID):
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    return products[product_id]


@app.put("/products/{product_id}", response_model=ProductRead, tags=["Product"])
def update_product(product_id: UUID, update: ProductUpdate):
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    stored = products[product_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    products[product_id] = ProductRead(**stored)
    return products[product_id]


@app.delete("/products/{product_id}", response_model=ProductRead, tags=["Product"])
def delete_product(product_id: UUID):
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    return products.pop(product_id)


# --------------------------------------------------------------------------
# Product -> Inventory & Category lookups
# --------------------------------------------------------------------------
@app.get("/products/{product_id}/inventory", response_model=InventoryRead, tags=["Product"])
def get_inventory_from_product(product_id: UUID):
    """Fetch the inventory details linked to a specific product."""
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")

    product = products[product_id]
    if not product.product_id:
        raise HTTPException(status_code=404, detail="This product has no linked inventory record")

    product_id = product.product_id
    if product_id not in inventories:
        raise HTTPException(status_code=404, detail="Linked inventory not found")

    return inventories[product_id]


@app.get("/products/{product_id}/category", response_model=CategoryRead, tags=["Product"])
def get_category_from_product(product_id: UUID):
    """Fetch the category details linked to a specific product."""
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")

    product = products[product_id]
    if not product.category_id:
        raise HTTPException(status_code=404, detail="This product has no linked category record")

    category_id = product.category_id
    if category_id not in categories:
        raise HTTPException(status_code=404, detail="Linked category not found")

    return categories[category_id]

# --------------------------------------------------------------------------
# Category endpoints
# --------------------------------------------------------------------------
@app.post("/categories", response_model=CategoryRead, status_code=201, tags=["Category"])
def create_category(category: CategoryCreate):
    category_read = CategoryRead(**category.model_dump())
    categories[category_read.category_id] = category_read
    return category_read


@app.get("/categories", response_model=List[CategoryRead], tags=["Category"])
def list_categories(name: Optional[str] = Query(None)):
    results = list(categories.values())
    if name:
        results = [c for c in results if c.name == name]
    return results


@app.get("/categories/{category_id}", response_model=CategoryRead, tags=["Category"])
def get_category(category_id: UUID):
    if category_id not in categories:
        raise HTTPException(status_code=404, detail="Category not found")
    return categories[category_id]


@app.put("/categories/{category_id}", response_model=CategoryRead, tags=["Category"])
def update_category(category_id: UUID, update: CategoryUpdate):
    if category_id not in categories:
        raise HTTPException(status_code=404, detail="Category not found")
    stored = categories[category_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    categories[category_id] = CategoryRead(**stored)
    return categories[category_id]


@app.delete("/categories/{category_id}", response_model=CategoryRead, tags=["Category"])
def delete_category(category_id: UUID):
    if category_id not in categories:
        raise HTTPException(status_code=404, detail="Category not found")
    return categories.pop(category_id)


# --------------------------------------------------------------------------
# Inventory endpoints
# --------------------------------------------------------------------------
@app.post("/inventories", response_model=InventoryRead, status_code=201, tags=["Inventory"])
def create_inventory(inventory: InventoryCreate):
    inventory_read = InventoryRead(**inventory.model_dump())
    inventories[inventory_read.product_id] = inventory_read
    return inventory_read


@app.get("/inventories", response_model=List[InventoryRead], tags=["Inventory"])
def list_inventories(product_id: Optional[UUID] = Query(None)):
    results = list(inventories.values())
    if product_id:
        results = [i for i in results if i.product_id == product_id]
    return results


@app.get("/inventories/{product_id}", response_model=InventoryRead, tags=["Inventory"])
def get_inventory(product_id: UUID):
    if product_id not in inventories:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventories[product_id]


@app.put("/inventories/{product_id}", response_model=InventoryRead, tags=["Inventory"])
def update_inventory(product_id: UUID, update: InventoryUpdate):
    if product_id not in inventories:
        raise HTTPException(status_code=404, detail="Inventory not found")
    stored = inventories[product_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    inventories[product_id] = InventoryRead(**stored)
    return inventories[product_id]


@app.delete("/inventories/{product_id}", response_model=InventoryRead, tags=["Inventory"])
def delete_inventory(product_id: UUID):
    if product_id not in inventories:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventories.pop(product_id)


# --------------------------------------------------------------------------
# Root
# --------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the Product/Category/Inventory API. See /docs for OpenAPI UI."}


# --------------------------------------------------------------------------
# Entrypoint
# --------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
