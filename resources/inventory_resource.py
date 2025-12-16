# from typing import Dict, List, Optional
# from uuid import UUID, uuid4
# from datetime import datetime
# from fastapi import HTTPException, Query
# from models.inventory import InventoryCreate, InventoryRead, InventoryUpdate

# # In-memory placeholder storage
# inventories: Dict[UUID, InventoryRead] = {}


# class InventoryResource:
#     """Resource class for Inventory CRUD operations"""

#     @staticmethod
#     def create_inventory(inventory: InventoryCreate) -> InventoryRead:
#         """Create a new inventory record"""

#         new_inventory = InventoryRead(
#             inventory_id=uuid4(),
#             product_id=inventory.product_id,
#             stock_quantity=inventory.stock_quantity,
#             warehouse_location=inventory.warehouse_location,
#             update_time=inventory.update_time,
#         )

#         inventories[new_inventory.inventory_id] = new_inventory
#         return new_inventory

#     @staticmethod
#     def get_inventories(
#         product_id: Optional[UUID] = Query(None),
#         warehouse_location: Optional[str] = Query(None),
#     ) -> List[InventoryRead]:
#         """Get all inventory records with optional filtering"""

#         results = list(inventories.values())

#         if product_id:
#             results = [inv for inv in results if inv.product_id == product_id]

#         if warehouse_location:
#             results = [
#                 inv for inv in results
#                 if inv.warehouse_location == warehouse_location
#             ]

#         return results

#     @staticmethod
#     def get_inventory_by_id(inventory_id: UUID) -> InventoryRead:
#         """Get a specific inventory record by its ID"""

#         if inventory_id not in inventories:
#             raise HTTPException(status_code=404, detail="Inventory not found")

#         return inventories[inventory_id]

#     @staticmethod
#     def update_inventory(
#         inventory_id: UUID,
#         inventory_update: InventoryUpdate
#     ) -> InventoryRead:
#         """Update an existing inventory record"""

#         if inventory_id not in inventories:
#             raise HTTPException(status_code=404, detail="Inventory not found")

#         existing = inventories[inventory_id]

#         # Apply partial updates
#         updated_inventory = existing.model_copy(
#             update=inventory_update.model_dump(exclude_unset=True)
#         )

#         inventories[inventory_id] = updated_inventory
#         return updated_inventory

#     @staticmethod
#     def delete_inventory(inventory_id: UUID) -> dict:
#         """Delete an inventory record by its ID"""

#         if inventory_id not in inventories:
#             raise HTTPException(status_code=404, detail="Inventory not found")

#         del inventories[inventory_id]
#         return {"detail": "Inventory deleted successfully"}

from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import HTTPException, Query

from models.inventory import InventoryCreate, InventoryRead, InventoryUpdate


class InventoryResource:
    """Resource class for Inventory CRUD operations (Cloud SQL backed)"""

    # get_connection is injected from main.py
    get_connection = None

    @staticmethod
    def create_inventory(inventory: InventoryCreate) -> InventoryRead:
        conn = InventoryResource.get_connection()
        inventory_id = str(uuid4())
        now = inventory.update_time or datetime.utcnow()

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO inventories
                (inventory_id, product_id, stock_quantity, warehouse_location, update_time)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    inventory_id,
                    str(inventory.product_id),
                    inventory.stock_quantity,
                    inventory.warehouse_location,
                    now,
                ),
            )
        conn.commit()

        return InventoryRead(
            inventory_id=UUID(inventory_id),
            product_id=inventory.product_id,
            stock_quantity=inventory.stock_quantity,
            warehouse_location=inventory.warehouse_location,
            update_time=now,
        )

    @staticmethod
    def get_inventories(
        product_id: Optional[UUID] = Query(None),
        warehouse_location: Optional[str] = Query(None),
    ) -> List[InventoryRead]:

        conn = InventoryResource.get_connection()

        query = "SELECT * FROM inventories WHERE 1=1"
        params = []

        if product_id:
            query += " AND product_id = %s"
            params.append(str(product_id))

        if warehouse_location:
            query += " AND warehouse_location = %s"
            params.append(warehouse_location)

        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()

        return [
            InventoryRead(
                inventory_id=UUID(row["inventory_id"]),
                product_id=UUID(row["product_id"]),
                stock_quantity=row["stock_quantity"],
                warehouse_location=row["warehouse_location"],
                update_time=row["update_time"],
            )
            for row in rows
        ]

    @staticmethod
    def get_inventory_by_id(inventory_id: UUID) -> InventoryRead:
        conn = InventoryResource.get_connection()

        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM inventories WHERE inventory_id = %s",
                (str(inventory_id),),
            )
            row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Inventory not found")

        return InventoryRead(
            inventory_id=UUID(row["inventory_id"]),
            product_id=UUID(row["product_id"]),
            stock_quantity=row["stock_quantity"],
            warehouse_location=row["warehouse_location"],
            update_time=row["update_time"],
        )

    @staticmethod
    def update_inventory(
        inventory_id: UUID,
        inventory_update: InventoryUpdate
    ) -> InventoryRead:

        updates = inventory_update.model_dump(exclude_unset=True)
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        updates["update_time"] = datetime.utcnow()

        set_clause = ", ".join(f"{k} = %s" for k in updates.keys())
        params = list(updates.values()) + [str(inventory_id)]

        conn = InventoryResource.get_connection()
        with conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE inventories
                SET {set_clause}
                WHERE inventory_id = %s
                """,
                params,
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Inventory not found")

        conn.commit()
        return InventoryResource.get_inventory_by_id(inventory_id)

    @staticmethod
    def delete_inventory(inventory_id: UUID) -> dict:
        conn = InventoryResource.get_connection()

        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM inventories WHERE inventory_id = %s",
                (str(inventory_id),),
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Inventory not found")

        conn.commit()
        return {"detail": "Inventory deleted successfully"}
