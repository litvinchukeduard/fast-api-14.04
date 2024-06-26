from typing import List

from fastapi import HTTPException, status

from sqlalchemy.orm import Session

from src.repository import ingredients as ingredient_repository
from src.repository import units as units_repository

from src.database.models import Ingredient
from src.schemas import IngredientModel


ERROR_INGREDIENT_ALREADY_EXISTS = "Ingredient with this name already exists"
INGREDIENT_NOT_FOUND = "Ingredient not found"


async def get_ingredients(skip: int, limit: int, db: Session) -> List[Ingredient]:
    return await ingredient_repository.get_ingredients(skip, limit, db)


async def get_ingredient(id: int, db: Session) -> Ingredient:
    ingredient = ingredient_repository.get_ingredient(id, db)
    if ingredient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=INGREDIENT_NOT_FOUND)


async def create_ingredient(body: IngredientModel, db: Session) -> Ingredient:
    await check_if_name_is_unique(body.name, db)
    
    units = await units_repository.get_units_by_ids(body.units, db)

    ingredient = Ingredient(
        name=body.name,
        units=units
    )
    
    return await ingredient_repository.create_ingredient(ingredient, db)


async def remove_ingredient(id: int, db: Session) -> Ingredient | None:
    return await ingredient_repository.remove_ingredient(id, db)


async def update_ingredient(id: int, body: IngredientModel, db: Session) -> Ingredient | None:
    await check_if_name_is_unique(body.name, db)

    units = await units_repository.get_units_by_ids(body.units, db)

    ingredient = await ingredient_repository.get_ingredient(id, db)
    if ingredient:
        ingredient.name = body.name
        ingredient.units = units
        await ingredient_repository.update_ingredient(ingredient, db)
    return ingredient


async def check_if_name_is_unique(name: str, db: Session) -> None:
    ingredient = await ingredient_repository.get_ingredient_by_name(name, db)
    if ingredient:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_INGREDIENT_ALREADY_EXISTS)
