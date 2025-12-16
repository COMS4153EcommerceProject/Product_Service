# from typing import Dict, List, Optional
# from uuid import UUID, uuid4
# from fastapi import HTTPException, Query
# from models.product import ProductCreate, ProductRead, ProductUpdate

# # In-memory placeholder storage
# products: Dict[UUID, ProductRead] = {}


# class ProductResource:
#     """Resource class for Product CRUD operations"""

#     @staticmethod
#     def create_product(product: ProductCreate) -> ProductRead:
#         """Create a new product"""

#         # Convert ProductCreate → ProductRead (server assigns product_id)
#         new_product = ProductRead(
#             product_id=uuid4(), #product.product_id,
#             name=product.name,
#             description=product.description,
#             price=product.price,
#             rating=product.rating,
#             category_id=product.category_id,
#             inventory_id=product.inventory_id,
#         )

#         products[new_product.product_id] = new_product
#         return new_product

#     @staticmethod
#     def get_products(
#         category_id: Optional[UUID] = Query(None),
#         inventory_id: Optional[UUID] = Query(None),
#     ) -> List[ProductRead]:
#         """Get all products, optionally filtered"""
#         results = list(products.values())

#         if category_id:
#             results = [p for p in results if p.category_id == category_id]

#         if inventory_id:
#             results = [p for p in results if p.inventory_id == inventory_id]

#         return results

#     @staticmethod
#     def get_product_by_id(product_id: UUID) -> ProductRead:
#         """Get a single product"""
#         if product_id not in products:
#             raise HTTPException(status_code=404, detail="Product not found")
#         return products[product_id]

#     @staticmethod
#     def update_product(product_id: UUID, product_update: ProductUpdate) -> ProductRead:
#         """Update an existing product"""
#         if product_id not in products:
#             raise HTTPException(status_code=404, detail="Product not found")

#         existing = products[product_id]

#         # Apply partial updates
#         updated_product = existing.model_copy(update=product_update.model_dump(exclude_unset=True))

#         products[product_id] = updated_product
#         return updated_product

#     @staticmethod
#     def delete_product(product_id: UUID) -> dict:
#         """Delete a product by ID"""
#         if product_id not in products:
#             raise HTTPException(status_code=404, detail="Product not found")

#         del products[product_id]
#         return {"detail": "Product deleted successfully"}
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import HTTPException, Query

from models.product import ProductCreate, ProductRead, ProductUpdate


class ProductResource:
    """Resource class for Product CRUD operations (Cloud SQL backed)"""

    # get_connection is injected from main.py
    get_connection = None

    @staticmethod
    def create_product(product: ProductCreate) -> ProductRead:
        conn = ProductResource.get_connection()
        product_id = str(uuid4())
        now = datetime.utcnow()

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO products
                (product_id, name, description, price, rating, category_id, inventory_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    product_id,
                    product.name,
                    product.description,
                    product.price,
                    product.rating,
                    str(product.category_id) if product.category_id else None,
                    str(product.inventory_id) if product.inventory_id else None,
                    now,
                    now,
                ),
            )

        conn.commit()
        conn.close()

        return ProductRead(
            product_id=product_id,
            name=product.name,
            description=product.description,
            price=product.price,
            rating=product.rating,
            category_id=product.category_id,
            inventory_id=product.inventory_id,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def get_products(
        category_id: Optional[UUID] = Query(None),
        inventory_id: Optional[UUID] = Query(None),
    ) -> List[ProductRead]:

        conn = ProductResource.get_connection()
        query = "SELECT * FROM products WHERE 1=1"
        params = []

        if category_id:
            query += " AND category_id=%s"
            params.append(str(category_id))

        if inventory_id:
            query += " AND inventory_id=%s"
            params.append(str(inventory_id))

        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()

        conn.close()
        return rows

    @staticmethod
    def get_product_by_id(product_id: UUID) -> ProductRead:
        conn = ProductResource.get_connection()

        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM products WHERE product_id=%s",
                (str(product_id),),
            )
            product = cur.fetchone()

        conn.close()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return product

    @staticmethod
    def update_product(product_id: UUID, product_update: ProductUpdate) -> ProductRead:
        updates = product_update.model_dump(exclude_unset=True)

        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        conn = ProductResource.get_connection()
        set_clause = ", ".join(f"{k}=%s" for k in updates.keys())
        values = [
            str(v) if isinstance(v, UUID) else v
            for v in updates.values()
        ]

        values.append(datetime.utcnow())
        values.append(str(product_id))

        with conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE products
                SET {set_clause}, updated_at=%s
                WHERE product_id=%s
                """,
                values,
            )

            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Product not found")

            cur.execute(
                "SELECT * FROM products WHERE product_id=%s",
                (str(product_id),),
            )
            product = cur.fetchone()

        conn.commit()
        conn.close()
        return product

    @staticmethod
    def delete_product(product_id: UUID) -> dict:
        conn = ProductResource.get_connection()

        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM products WHERE product_id=%s",
                (str(product_id),),
            )

            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Product not found")

        conn.commit()
        conn.close()
        return {"detail": "Product deleted successfully"}
