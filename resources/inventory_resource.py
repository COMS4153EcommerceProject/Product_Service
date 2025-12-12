from typing import Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import HTTPException, Query
from models.inventory import InventoryCreate, InventoryRead, InventoryUpdate

# In-memory placeholder storage
inventories: Dict[UUID, InventoryRead] = {}


class InventoryResource:
    """Resource class for Inventory CRUD operations"""

    @staticmethod
    def create_inventory(inventory: InventoryCreate) -> InventoryRead:
        """Create a new inventory record"""

        new_inventory = InventoryRead(
            inventory_id=uuid4(),
            product_id=inventory.product_id,
            stock_quantity=inventory.stock_quantity,
            warehouse_location=inventory.warehouse_location,
            update_time=inventory.update_time,
        )

        inventories[new_inventory.inventory_id] = new_inventory
        return new_inventory

    @staticmethod
    def get_inventories(
        product_id: Optional[UUID] = Query(None),
        warehouse_location: Optional[str] = Query(None),
    ) -> List[InventoryRead]:
        """Get all inventory records with optional filtering"""

        results = list(inventories.values())

        if product_id:
            results = [inv for inv in results if inv.product_id == product_id]

        if warehouse_location:
            results = [
                inv for inv in results
                if inv.warehouse_location == warehouse_location
            ]

        return results

    @staticmethod
    def get_inventory_by_id(inventory_id: UUID) -> InventoryRead:
        """Get a specific inventory record by its ID"""

        if inventory_id not in inventories:
            raise HTTPException(status_code=404, detail="Inventory not found")

        return inventories[inventory_id]

    @staticmethod
    def update_inventory(
        inventory_id: UUID,
        inventory_update: InventoryUpdate
    ) -> InventoryRead:
        """Update an existing inventory record"""

        if inventory_id not in inventories:
            raise HTTPException(status_code=404, detail="Inventory not found")

        existing = inventories[inventory_id]

        # Apply partial updates
        updated_inventory = existing.model_copy(
            update=inventory_update.model_dump(exclude_unset=True)
        )

        inventories[inventory_id] = updated_inventory
        return updated_inventory

    @staticmethod
    def delete_inventory(inventory_id: UUID) -> dict:
        """Delete an inventory record by its ID"""

        if inventory_id not in inventories:
            raise HTTPException(status_code=404, detail="Inventory not found")

        del inventories[inventory_id]
        return {"detail": "Inventory deleted successfully"}
