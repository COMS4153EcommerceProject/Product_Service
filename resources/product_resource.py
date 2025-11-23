from typing import Dict, List, Optional
from uuid import UUID, uuid4
from fastapi import HTTPException, Query
from models.product import ProductCreate, ProductRead, ProductUpdate

# In-memory placeholder storage
products: Dict[UUID, ProductRead] = {}


class ProductResource:
    """Resource class for Product CRUD operations"""

    @staticmethod
    def create_product(product: ProductCreate) -> ProductRead:
        """Create a new product"""

        # Convert ProductCreate → ProductRead (server assigns product_id)
        new_product = ProductRead(
            product_id=uuid4(), #product.product_id,
            name=product.name,
            description=product.description,
            price=product.price,
            rating=product.rating,
            category_id=product.category_id,
            inventory_id=product.inventory_id,
        )

        products[new_product.product_id] = new_product
        return new_product

    @staticmethod
    def get_products(
        category_id: Optional[UUID] = Query(None),
        inventory_id: Optional[UUID] = Query(None),
    ) -> List[ProductRead]:
        """Get all products, optionally filtered"""
        results = list(products.values())

        if category_id:
            results = [p for p in results if p.category_id == category_id]

        if inventory_id:
            results = [p for p in results if p.inventory_id == inventory_id]

        return results

    @staticmethod
    def get_product_by_id(product_id: UUID) -> ProductRead:
        """Get a single product"""
        if product_id not in products:
            raise HTTPException(status_code=404, detail="Product not found")
        return products[product_id]

    @staticmethod
    def update_product(product_id: UUID, product_update: ProductUpdate) -> ProductRead:
        """Update an existing product"""
        if product_id not in products:
            raise HTTPException(status_code=404, detail="Product not found")

        existing = products[product_id]

        # Apply partial updates
        updated_product = existing.model_copy(update=product_update.model_dump(exclude_unset=True))

        products[product_id] = updated_product
        return updated_product

    @staticmethod
    def delete_product(product_id: UUID) -> dict:
        """Delete a product by ID"""
        if product_id not in products:
            raise HTTPException(status_code=404, detail="Product not found")

        del products[product_id]
        return {"detail": "Product deleted successfully"}
