from __future__ import annotations
import os
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query

# Import your Pydantic models
from models.product import ProductCreate, ProductRead, ProductUpdate
from models.category import CategoryCreate, CategoryRead, CategoryUpdate
from models.inventory import InventoryCreate, InventoryRead, InventoryUpdate

# Import your resource classes
from resources.product_resource import ProductResource
from resources.category_resource import CategoryResource
from resources.inventory_resource import InventoryResource

import pymysql
from pymysql.cursors import DictCursor

# --------------------------------------------------------------------------
# CONFIGURATION for Cloud SQL + Local Development
# --------------------------------------------------------------------------

def get_db_connection():
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )
# def get_db_connection():
#     """
#     Connect to MySQL using either:
#     - Cloud SQL Unix socket (Cloud Run)
#     - TCP host (Local dev)
#     """

#     # Cloud Run socket path
#     db_socket = os.getenv("DB_SOCKET")  # e.g. "/cloudsql/project:region:instance"
#     db_host = os.getenv("DB_HOST")      # e.g. "127.0.0.1" for local dev
#     db_user = os.getenv("DB_USER")
#     db_pass = os.getenv("DB_PASSWORD")
#     db_name = os.getenv("DB_NAME")

#     if db_socket:
#         # Cloud Run connection
#         return pymysql.connect(
#             unix_socket=db_socket,
#             user=db_user,
#             password=db_pass,
#             database=db_name,
#             cursorclass=DictCursor,
#         )
#     else:
#         # Local development over TCP/IP
#         return pymysql.connect(
#             host=db_host or "127.0.0.1",
#             port=3306,
#             user=db_user,
#             password=db_pass,
#             database=db_name,
#             cursorclass=DictCursor,
#         )


# Make database connection available to Resource classes
ProductResource.get_connection = staticmethod(get_db_connection)
CategoryResource.get_connection = staticmethod(get_db_connection)
InventoryResource.get_connection = staticmethod(get_db_connection)

# --------------------------------------------------------------------------
# FastAPI App
# --------------------------------------------------------------------------

port = int(os.environ.get("FASTAPIPORT", 8003))

app = FastAPI(
    title="Product/Category/Inventory API",
    description="FastAPI Microservice backed by Cloud SQL.",
    version="0.3.0",
)

# --------------------------------------------------------------------------
# Product endpoints
# --------------------------------------------------------------------------

@app.post("/products", response_model=ProductRead, status_code=201, tags=["Product"])
def create_product(product: ProductCreate):
    return ProductResource.create_product(product)


@app.get("/products", response_model=List[ProductRead], tags=["Product"])
def list_products(
    category_id: Optional[UUID] = Query(None),
    inventory_id: Optional[UUID] = Query(None),
):
    return ProductResource.get_products(category_id=category_id, inventory_id=inventory_id)


@app.get("/products/{product_id}", response_model=ProductRead, tags=["Product"])
def get_product(product_id: UUID):
    return ProductResource.get_product_by_id(product_id)


@app.put("/products/{product_id}", response_model=ProductRead, tags=["Product"])
def update_product(product_id: UUID, update: ProductUpdate):
    return ProductResource.update_product(product_id, update)


@app.delete("/products/{product_id}", response_model=dict, tags=["Product"])
def delete_product(product_id: UUID):
    return ProductResource.delete_product(product_id)

# --------------------------------------------------------------------------
# Category endpoints
# --------------------------------------------------------------------------

@app.post("/categories", response_model=CategoryRead, status_code=201, tags=["Category"])
def create_category(category: CategoryCreate):
    return CategoryResource.create_category(category)


@app.get("/categories", response_model=List[CategoryRead], tags=["Category"])
def list_categories(name: Optional[str] = Query(None)):
    return CategoryResource.get_categories(name=name)


@app.get("/categories/{category_id}", response_model=CategoryRead, tags=["Category"])
def get_category(category_id: UUID):
    return CategoryResource.get_category_by_id(category_id)


@app.put("/categories/{category_id}", response_model=CategoryRead, tags=["Category"])
def update_category(category_id: UUID, update: CategoryUpdate):
    return CategoryResource.update_category(category_id, update)


@app.delete("/categories/{category_id}", response_model=dict, tags=["Category"])
def delete_category(category_id: UUID):
    return CategoryResource.delete_category(category_id)

# --------------------------------------------------------------------------
# Inventory endpoints
# --------------------------------------------------------------------------

@app.post("/inventories", response_model=InventoryRead, status_code=201, tags=["Inventory"])
def create_inventory(inventory: InventoryCreate):
    return InventoryResource.create_inventory(inventory)


@app.get("/inventories", response_model=List[InventoryRead], tags=["Inventory"])
def list_inventories(
    product_id: Optional[UUID] = Query(None),
    warehouse_location: Optional[str] = Query(None),
):
    return InventoryResource.get_inventories(product_id=product_id, warehouse_location=warehouse_location)


@app.get("/inventories/{inventory_id}", response_model=InventoryRead, tags=["Inventory"])
def get_inventory(inventory_id: UUID):
    return InventoryResource.get_inventory_by_id(inventory_id)


@app.put("/inventories/{inventory_id}", response_model=InventoryRead, tags=["Inventory"])
def update_inventory(inventory_id: UUID, update: InventoryUpdate):
    return InventoryResource.update_inventory(inventory_id, update)


@app.delete("/inventories/{inventory_id}", response_model=dict, tags=["Inventory"])
def delete_inventory(inventory_id: UUID):
    return InventoryResource.delete_inventory(inventory_id)

# --------------------------------------------------------------------------
# Root
# --------------------------------------------------------------------------

@app.get("/")
def root():
    return {"message": "Product/Category/Inventory API is running. See /docs."}

# --------------------------------------------------------------------------
# Entrypoint
# --------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port)
