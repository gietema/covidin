import json
from typing import Union
import plotly
import pandas as pd
import plotly.graph_objs as go
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

templates = Jinja2Templates(directory="templates")


def selectpage(request: Request) -> templates.TemplateResponse:
    df = app.state.data
    return templates.TemplateResponse(
        "index.html",
        {
            "slugs": df.municipality_slug.tolist(),
            "municipality_names": df.sort_values(by="municipality_slug").municipality_name.unique().tolist(),
            "municipality_slugs": df.sort_values(by="municipality_slug").municipality_slug.unique().tolist(),
            "last_date": df.date.tolist()[-1],
            "request": request,
        },
    )


async def select(request: Request) -> RedirectResponse:
    data = await request.form()
    return RedirectResponse(url=f"/{data['municipality_slug']}")


def homepage(request: Request) -> Union[templates.TemplateResponse, RedirectResponse]:
    df = app.state.data
    municipality_name = request.path_params["municipality_name"]

    if municipality_name is None:
        return RedirectResponse(url="/")

    if municipality_name not in df.municipality_slug.tolist():
        return RedirectResponse(url="/")

    df = df[df.municipality_slug == municipality_name]
    df["new_per_day"] = [d - d1 for d, d1 in zip(df.total_reported, [0] + df.total_reported.tolist()[:-1])]
    df["rolling_average_7_days"] = df.new_per_day.rolling(window=7).mean()
    new_today = df.new_per_day.tolist()[-1]
    last_date = df.date.tolist()[-1]

    bar = go.Bar(
        x=df.date.tolist(), y=df.new_per_day.tolist(), name="New confirmed cases per day", marker_color="royalblue"
    )
    line = go.Scatter(
        x=df.date.tolist(),
        y=df.rolling_average_7_days.tolist(),
        name="7-day rolling average",
        line=dict(color="#df5b56", width=2, dash="solid"),
    )
    graph = json.dumps([bar, line], cls=plotly.utils.PlotlyJSONEncoder)

    return templates.TemplateResponse(
        "show.html",
        {
            "request": request,
            "municipality_name": df.municipality_name.iloc[0],
            "new_today": new_today,
            "new_per_day": df.new_per_day.tolist(),
            "last_date": last_date,
            "graph": graph,
        },
    )


routes = [
    Route("/", endpoint=selectpage),
    Route("/select", endpoint=select, methods=["post"]),
    Route("/{municipality_name:str}", endpoint=homepage, methods=["post", "get"]),
    Mount("/static", StaticFiles(directory="static"), name="static"),
]

app = Starlette(debug=False, routes=routes)
app.state.data = pd.read_csv("static/data/data.csv")
