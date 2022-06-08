from fastapi import FastAPI, APIRouter, Query, HTTPException, Request
from fastapi.templating import Jinja2Templates
from typing import Optional, Any
from pathlib import Path

from starlette.templating import _TemplateResponse

from app.schemas import Recipe, RecipeSearchResult, RecipeCreate

from app.recipe_data import RECIPES

BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))

app = FastAPI(
    title="Recipe API", openapi_url="/openapi.json"
)

# 2
api_router = APIRouter()


@app.get("/")
async def root(request: Request) -> _TemplateResponse:
    """
    ROOT GET
    :return:
    """
    return TEMPLATES.TemplateResponse(
        "index.html",
        {"request": request, "recipes": RECIPES}
    )


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


# 3
@api_router.get("/", status_code=200)
def root() -> dict:
    """
    Root Get
    """
    return {"msg": "Hello, World!"}


@api_router.get("/recipe/{recipe_id}", status_code=200, response_model=Recipe)
async def fetch_recipe(*, recipe_id: int) -> dict:
    """
    Fetch a single receipt by its id
    :param recipe_id:
    :return:
    """

    # print(type(recipe_id))

    result = [recipe for recipe in RECIPES if recipe['id'] == recipe_id]

    if not result:

        raise HTTPException(
            status_code=404, detail=f"Recipe with ID {recipe_id} not found."
        )

    return result[0]


@api_router.get("/search", status_code=200, response_model=RecipeSearchResult)
async def search_recipes(
        keyword: Optional[str] = Query(None, min_length=3, example='Chicken'),
        max_results: Optional[int] = 10
) -> dict:
    """
    Search for recipes based on label keyword
    :param max_results:
    :param keyword:
    :param max_result:
    :return:
    """

    if not keyword:
        return {"results": RECIPES[:max_results]}

    results = filter(lambda recipe: keyword.lower() in recipe['label'].lower(), RECIPES)

    return {"results": list(results)[:max_results]}


# POST REQUESTS

@api_router.post("/recipe/", status_code=201, response_model=Recipe)
async def create_recipe(*, receipt_in: RecipeCreate) -> Recipe:
    """
    Receive Recipe and save it
    :param receipt_in:
    :return:
    """
    new_entry_id = len(RECIPES) + 1

    recipe_entry = Recipe(
        id=new_entry_id,
        label=receipt_in.label,
        source=receipt_in.source,
        url=receipt_in.url
    )
    RECIPES.append(recipe_entry.dict())

    return recipe_entry


# router
app.include_router(api_router)

# instance
if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
