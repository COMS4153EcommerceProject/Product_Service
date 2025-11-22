from typing import Dict, List, Optional
from uuid import UUID
from fastapi import HTTPException, Query
from models.category import CategoryCreate, CategoryRead, CategoryUpdate

# In-memory placeholder storage
categories: Dict[UUID, CategoryRead] = {}

class CategoryResource:
    """Resource class for Category CRUD operations"""

    @staticmethod
    def create_category(category: CategoryCreate) -> CategoryRead:
        """Create a new category"""
        # For now, return NOT IMPLEMENTED
        raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")

    @staticmethod
    def get_categories(name: Optional[str] = Query(None)) -> List[CategoryRead]:
        """Get all categories with optional filtering by name"""
        # For now, return NOT IMPLEMENTED
        raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")

    @staticmethod
    def get_category_by_id(category_id: UUID) -> CategoryRead:
        """Get a category by its ID"""
        # For now, return NOT IMPLEMENTED
        raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")

    @staticmethod
    def update_category(category_id: UUID, category_update: CategoryUpdate) -> CategoryRead:
        """Update an existing category"""
        # For now, return NOT IMPLEMENTED
        raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")

    @staticmethod
    def delete_category(category_id: UUID) -> dict:
        """Delete a category by its ID"""
        # For now, return NOT IMPLEMENTED
        raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")
