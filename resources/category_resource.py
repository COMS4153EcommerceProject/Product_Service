# from typing import Dict, List, Optional
# from uuid import UUID, uuid4
# from datetime import datetime
# from fastapi import HTTPException, Query
# from models.category import CategoryCreate, CategoryRead, CategoryUpdate

# # In-memory placeholder storage
# categories: Dict[UUID, CategoryRead] = {}


# class CategoryResource:
#     """Resource class for Category CRUD operations"""

#     @staticmethod
#     def create_category(category: CategoryCreate) -> CategoryRead:
#         """Create a new category"""

#         new_category = CategoryRead(
#             category_id=uuid4(),
#             name=category.name,
#             description=category.description,
#         )

#         categories[new_category.category_id] = new_category
#         return new_category

#     @staticmethod
#     def get_categories(name: Optional[str] = Query(None)) -> List[CategoryRead]:
#         """Get all categories with optional filtering by name"""

#         results = list(categories.values())

#         if name:
#             results = [
#                 c for c in results
#                 if c.name.lower() == name.lower()
#             ]

#         return results

#     @staticmethod
#     def get_category_by_id(category_id: UUID) -> CategoryRead:
#         """Get a category by its ID"""

#         if category_id not in categories:
#             raise HTTPException(status_code=404, detail="Category not found")

#         return categories[category_id]

#     @staticmethod
#     def update_category(
#         category_id: UUID,
#         category_update: CategoryUpdate
#     ) -> CategoryRead:
#         """Update an existing category"""

#         if category_id not in categories:
#             raise HTTPException(status_code=404, detail="Category not found")

#         existing = categories[category_id]

#         updated_category = existing.model_copy(
#             update={
#                 **category_update.model_dump(exclude_unset=True),
#                 "updated_at": datetime.utcnow(),
#             }
#         )

#         categories[category_id] = updated_category
#         return updated_category

#     @staticmethod
#     def delete_category(category_id: UUID) -> dict:
#         """Delete a category by its ID"""

#         if category_id not in categories:
#             raise HTTPException(status_code=404, detail="Category not found")

#         del categories[category_id]
#         return {"detail": "Category deleted successfully"}

from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import HTTPException, Query

from models.category import CategoryCreate, CategoryRead, CategoryUpdate
from db import get_db_connection


class CategoryResource:
    """Resource class for Category CRUD operations (DB-based)"""

    @staticmethod
    def create_category(category: CategoryCreate) -> CategoryRead:
        category_id = str(uuid4())
        now = datetime.utcnow()

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO categories
                    (category_id, name, description, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        category_id,
                        category.name,
                        category.description,
                        now,
                        now,
                    ),
                )
            conn.commit()
        except Exception:
            raise HTTPException(status_code=400, detail="Category already exists")
        finally:
            conn.close()

        return CategoryRead(
            category_id=UUID(category_id),
            name=category.name,
            description=category.description,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def get_categories(name: Optional[str] = Query(None)) -> List[CategoryRead]:
        query = "SELECT * FROM categories WHERE 1=1"
        params = []

        if name:
            query += " AND LOWER(name) = LOWER(%s)"
            params.append(name)

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
        finally:
            conn.close()

        return [
            CategoryRead(
                category_id=UUID(row["category_id"]),
                name=row["name"],
                description=row["description"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    @staticmethod
    def get_category_by_id(category_id: UUID) -> CategoryRead:
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM categories WHERE category_id = %s",
                    (str(category_id),),
                )
                row = cur.fetchone()
        finally:
            conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Category not found")

        return CategoryRead(
            category_id=UUID(row["category_id"]),
            name=row["name"],
            description=row["description"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def update_category(
        category_id: UUID,
        category_update: CategoryUpdate
    ) -> CategoryRead:

        updates = category_update.model_dump(exclude_unset=True)
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        updates["updated_at"] = datetime.utcnow()

        set_clause = ", ".join(f"{k} = %s" for k in updates.keys())
        params = list(updates.values()) + [str(category_id)]

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE categories
                    SET {set_clause}
                    WHERE category_id = %s
                    """,
                    params,
                )
                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Category not found")
            conn.commit()
        finally:
            conn.close()

        return CategoryResource.get_category_by_id(category_id)

    @staticmethod
    def delete_category(category_id: UUID) -> dict:
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM categories WHERE category_id = %s",
                    (str(category_id),),
                )
                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Category not found")
            conn.commit()
        finally:
            conn.close()

        return {"detail": "Category deleted successfully"}
