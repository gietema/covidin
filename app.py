import json
import plotly
import pandas as pd
import plotly.graph_objs as go
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles


templates = Jinja2Templates(directory='templates')


def homepage(request):
    municipality_name = request.path_params['municipality_name']
    df = app.state.data
    df = df[df.municipality_slug == municipality_name]
    df["new_per_day"] = [d-d1 for d, d1 in zip(df.total_reported, [0] + df.total_reported.tolist()[:-1])]
    new_today = df.new_per_day.tolist()[-1]

    trace = go.Bar(
        x = df.date.tolist(),
        y = df.new_per_day.tolist(),
    )
    graph = json.dumps([trace], cls=plotly.utils.PlotlyJSONEncoder)

    return templates.TemplateResponse('index.html', {
        'request': request,
        'municipality_name': df.municipality_name.iloc[0],
        'new_today': new_today,
        'new_per_day': df.new_per_day.tolist(),
        'graph': graph
    })

routes = [
    Route('/{municipality_name:str}', endpoint=homepage),
    Mount('/static', StaticFiles(directory='static'), name='static')
]

app = Starlette(debug=True, routes=routes)
app.state.data = pd.read_csv("static/data/data.csv")