from ludic.catalog.headers import H1

from src.components import Hello
from src.main import app
from src.pages import Page


@app.get("/")
async def homepage() -> Page:
    return Page(
        H1("ludic Homepage"),
        Hello(name="Stranger"),
    )
