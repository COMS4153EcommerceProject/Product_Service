from typing import Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import HTTPException, Query
from models.category import CategoryCreate, CategoryRead, CategoryUpdate

# In-memory placeholder storage
categories: Dict[UUID, CategoryRead] = {}


class CategoryResource:
    """Resource class for Category CRUD operations"""

    @staticmethod
    def create_category(category: CategoryCreate) -> CategoryRead:
        """Create a new category"""

        new_category = CategoryRead(
            category_id=uuid4(),
            name=category.name,
            description=category.description,
        )

        categories[new_category.category_id] = new_category
        return new_category

    @staticmethod
    def get_categories(name: Optional[str] = Query(None)) -> List[CategoryRead]:
        """Get all categories with optional filtering by name"""

        results = list(categories.values())

        if name:
            results = [
                c for c in results
                if c.name.lower() == name.lower()
            ]

        return results

    @staticmethod
    def get_category_by_id(category_id: UUID) -> CategoryRead:
        """Get a category by its ID"""

        if category_id not in categories:
            raise HTTPException(status_code=404, detail="Category not found")

        return categories[category_id]

    @staticmethod
    def update_category(
        category_id: UUID,
        category_update: CategoryUpdate
    ) -> CategoryRead:
        """Update an existing category"""

        if category_id not in categories:
            raise HTTPException(status_code=404, detail="Category not found")

        existing = categories[category_id]

        updated_category = existing.model_copy(
            update={
                **category_update.model_dump(exclude_unset=True),
                "updated_at": datetime.utcnow(),
            }
        )

        categories[category_id] = updated_category
        return updated_category

    @staticmethod
    def delete_category(category_id: UUID) -> dict:
        """Delete a category by its ID"""

        if category_id not in categories:
            raise HTTPException(status_code=404, detail="Category not found")

        del categories[category_id]
        return {"detail": "Category deleted successfully"}
