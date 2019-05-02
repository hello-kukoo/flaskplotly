from flask import Flask, render_template
import json
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from plotly import tools

import numpy as np
import pandas as pd
import urllib

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


def create_line():
    count = 500
    xScale = np.linspace(0, 100, count)
    yScale = np.random.randn(count)

    trace = go.Scatter(x=xScale, y=yScale)
    figure = [trace]
    return figure


@app.route('/showLineChart')
def line():
    graph = create_line()
    graphJSON = json.dumps(graph, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('graph.html',
                           graphJSON=graphJSON)


def create_multiLine():
    count = 500
    xScale = np.linspace(0, 100, count)
    y0_scale = np.random.randn(count)
    y1_scale = np.random.randn(count)
    y2_scale = np.random.randn(count)

    # Create traces
    trace0 = go.Scatter(
        x=xScale,
        y=y0_scale
    )
    trace1 = go.Scatter(
        x=xScale,
        y=y1_scale
    )
    trace2 = go.Scatter(
        x=xScale,
        y=y2_scale
    )
    figure = [trace0, trace1, trace2]
    return figure


@app.route('/showMultiChart')
def multiLine():
    figure = create_multiLine()
    graphJSON = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('graph.html',
                           graphJSON=graphJSON)


def create_surface():
    # Read data from a csv
    z_data = pd.read_csv(
        'https://raw.githubusercontent.com/plotly/datasets/master/api_docs/mt_bruno_elevation.csv')

    figure = [
        go.Surface(
            z=z_data.as_matrix()
        )
    ]
    layout = go.Layout(
        title='Mt Bruno Elevation',
        autosize=False,
        width=800,
        height=800,
        margin=dict(
            l=65,
            r=50,
            b=65,
            t=90
        )
    )
    return figure, layout


@app.route('/plot3d')
def plot3D():
    figure, layout = create_surface()
    graphJSON = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
    layoutJSON = json.dumps(layout, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('graph.html',
                           graphJSON=graphJSON,
                           layoutJSON=layoutJSON)


def create_surface_contours():
    # Read data from a csv
    z_data = pd.read_csv(
        'https://raw.githubusercontent.com/plotly/datasets/master/api_docs/mt_bruno_elevation.csv')

    figure = [
        go.Surface(
            z=z_data.as_matrix(),
            contours=go.surface.Contours(
                z=go.surface.contours.Z(
                    show=True,
                    usecolormap=True,
                    highlightcolor="#42f462",
                    project=dict(z=True)
                )
            )
        )
    ]
    layout = go.Layout(
        title='3D视图',
        autosize=False,
        scene=dict(camera=dict(eye=dict(x=1.87, y=0.88, z=-0.64))),
        width=800,
        height=800,
        margin=dict(
            l=65,
            r=50,
            b=65,
            t=90
        )
    )
    return figure, layout

@app.route('/plot3dcontours')
def plot3DContours():
    figure, layout = create_surface_contours()
    graphJSON = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
    layoutJSON = json.dumps(layout, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('graph.html',
                           graphJSON=graphJSON,
                           layoutJSON=layoutJSON)


def create_sankey():
    url = 'https://raw.githubusercontent.com/plotly/plotly.js/master/test/image/mocks/sankey_energy.json'
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())

    data_trace = dict(
        type='sankey',
        # width=1118,
        # height=1000,
        domain=dict(
            x=[0, 1],
            y=[0, 1]
        ),
        orientation="h",
        valueformat=".0f",
        valuesuffix="TWh",
        node=dict(
            pad=15,
            thickness=15,
            line=dict(
                color="black",
                width=0.5
            ),
            label=data['data'][0]['node']['label'],
            color=data['data'][0]['node']['color']
        ),
        link=dict(
            source=data['data'][0]['link']['source'],
            target=data['data'][0]['link']['target'],
            value=data['data'][0]['link']['value'],
            label=data['data'][0]['link']['label']
        )
    )

    layout = dict(
        title="Energy forecast for 2050<br>Source: Department of Energy & Climate Change, Tom Counsell via <a href='https://bost.ocks.org/mike/sankey/'>Mike Bostock</a>",
        font=dict(
            size=10
        )
    )
    figure = [data_trace]
    return figure, layout


@app.route('/sankey')
def sankeyDiagram():
    figure, layout = create_sankey()
    graphJSON = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
    layoutJSON = json.dumps(layout, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('graph.html',
                           graphJSON=graphJSON,
                           layoutJSON=layoutJSON)

def create_bar_line():
    y_saving = [1.3586, 2.2623000000000002, 4.9821999999999997, 6.5096999999999996,
                7.4812000000000003, 7.5133000000000001, 15.2148, 17.520499999999998]
    y_net_worth = [93453.919999999998, 81666.570000000007, 69889.619999999995,
                   78381.529999999999, 141395.29999999999, 92969.020000000004,
                   66090.179999999993, 122379.3]
    x_saving = ['Japan', 'United Kingdom', 'Canada', 'Netherlands',
                'United States', 'Belgium', 'Sweden', 'Switzerland']
    x_net_worth = ['Japan', 'United Kingdom', 'Canada', 'Netherlands',
                   'United States', 'Belgium', 'Sweden', 'Switzerland']
    trace0 = go.Bar(
        x=y_saving,
        y=x_saving,
        marker=dict(
            color='rgba(50, 171, 96, 0.6)',
            line=dict(
                color='rgba(50, 171, 96, 1.0)',
                width=1),
        ),
        name='Household savings, percentage of household disposable income',
        orientation='h',
    )
    trace1 = go.Scatter(
        x=y_net_worth,
        y=x_net_worth,
        mode='lines+markers',
        line=dict(
            color='rgb(128, 0, 128)'),
        name='Household net worth, Million USD/capita',
    )
    layout = dict(
        title='Household savings & net worth for eight OECD countries',
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=True,
            domain=[0, 0.85],
        ),
        yaxis2=dict(
            showgrid=False,
            showline=True,
            showticklabels=False,
            linecolor='rgba(102, 102, 102, 0.8)',
            linewidth=2,
            domain=[0, 0.85],
        ),
        xaxis=dict(
            zeroline=False,
            showline=False,
            showticklabels=True,
            showgrid=True,
            domain=[0, 0.42],
        ),
        xaxis2=dict(
            zeroline=False,
            showline=False,
            showticklabels=True,
            showgrid=True,
            domain=[0.47, 1],
            side='top',
            dtick=25000,
        ),
        legend=dict(
            x=0.029,
            y=1.038,
            font=dict(
                size=10,
            ),
        ),
        margin=dict(
            l=100,
            r=20,
            t=70,
            b=70,
        ),
        paper_bgcolor='rgb(248, 248, 255)',
        plot_bgcolor='rgb(248, 248, 255)',
    )

    annotations = []

    y_s = np.round(y_saving, decimals=2)
    y_nw = np.rint(y_net_worth)

    # Adding labels
    for ydn, yd, xd in zip(y_nw, y_s, x_saving):
        # labeling the scatter savings
        annotations.append(dict(xref='x2', yref='y2',
                                y=xd, x=ydn - 20000,
                                text='{:,}'.format(ydn) + 'M',
                                font=dict(family='Arial', size=12,
                                          color='rgb(128, 0, 128)'),
                                showarrow=False))
        # labeling the bar net worth
        annotations.append(dict(xref='x1', yref='y1',
                                y=xd, x=yd + 3,
                                text=str(yd) + '%',
                                font=dict(family='Arial', size=12,
                                          color='rgb(50, 171, 96)'),
                                showarrow=False))
    # Source
    annotations.append(dict(xref='paper', yref='paper',
                            x=-0.2, y=-0.109,
                            text='OECD "' +
                            '(2015), Household savings (indicator), ' +
                            'Household net worth (indicator). doi: ' +
                            '10.1787/cfc6f499-en (Accessed on 05 June 2015)',
                            font=dict(family='Arial', size=10,
                                      color='rgb(150,150,150)'),
                            showarrow=False))

    layout['annotations'] = annotations

    # Creating two subplots
    fig = tools.make_subplots(rows=1, cols=2, specs=[[{}, {}]], shared_xaxes=True,
                              shared_yaxes=False, vertical_spacing=0.001)

    fig.append_trace(trace0, 1, 1)
    fig.append_trace(trace1, 1, 2)

    fig['layout'].update(layout)
    return fig.data, fig.layout

@app.route('/barandline')
def mixBarandLine():
    figure, layout = create_bar_line()
    graphJSON = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
    layoutJSON = json.dumps(layout, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('graph.html',
                           graphJSON=graphJSON,
                           layoutJSON=layoutJSON)

def create_sunburst():
    df1 = pd.read_csv(
        'https://raw.githubusercontent.com/plotly/datasets/718417069ead87650b90472464c7565dc8c2cb1c/sunburst-coffee-flavors-complete.csv')
    df2 = pd.read_csv(
        'https://raw.githubusercontent.com/plotly/datasets/718417069ead87650b90472464c7565dc8c2cb1c/coffee-flavors.csv')

    trace1 = go.Sunburst(
        ids=df1.ids,
        labels=df1.labels,
        parents=df1.parents,
        domain=dict(column=0, row=0)
    )

    trace2 = go.Sunburst(
        ids=df2.ids,
        labels=df2.labels,
        parents=df2.parents,
        domain=dict(column=1, row=0),
        maxdepth=2
    )

    trace3 = go.Sunburst(
        ids=[
            "North America", "Europe", "Australia", "North America - Football", "Soccer",
            "North America - Rugby", "Europe - Football", "Rugby",
            "Europe - American Football", "Australia - Football", "Association",
            "Australian Rules", "Autstralia - American Football", "Australia - Rugby",
            "Rugby League", "Rugby Union"
        ],
        labels=[
            "North<br>America", "Europe", "Australia", "Football", "Soccer", "Rugby",
            "Football", "Rugby", "American<br>Football", "Football", "Association",
            "Australian<br>Rules", "American<br>Football", "Rugby", "Rugby<br>League",
            "Rugby<br>Union"
        ],
        parents=[
            "", "", "", "North America", "North America", "North America", "Europe",
            "Europe", "Europe", "Australia", "Australia - Football", "Australia - Football",
            "Australia - Football", "Australia - Football", "Australia - Rugby",
            "Australia - Rugby"
        ],
        outsidetextfont={"size": 20, "color": "#377eb8"},
        leaf={"opacity": 0.4},
        marker={"line": {"width": 2}},
        domain=dict(column=0, row=1),
    )

    trace4 = go.Sunburst(
        labels=["Eve", "Cain", "Seth", "Enos",
                "Noam", "Abel", "Awan", "Enoch", "Azura"],
        parents=["", "Eve", "Eve", "Seth",
                 "Seth", "Eve", "Eve", "Awan", "Eve"],
        values=[10, 14, 12, 10, 2, 6, 6, 4, 4],
        outsidetextfont={"size": 20, "color": "#377eb8"},
        marker={"line": {"width": 2}},
        domain=dict(column=1, row=1),
    )

    layout = go.Layout(
        width=1500,
        height=900,
        grid=go.layout.Grid(columns=2, rows=2),
        margin=go.layout.Margin(t=0, l=0, r=0, b=0),
        sunburstcolorway=[
            "#636efa", "#EF553B", "#00cc96", "#ab63fa", "#19d3f3",
            "#e763fa", "#FECB52", "#FFA15A", "#FF6692", "#B6E880",
        ],
        extendsunburstcolors=True
    )

    figure = [trace1, trace2, trace3, trace4]
    return figure, layout

@app.route('/sunburst')
def sunburst():
    figure, layout = create_sunburst()
    graphJSON = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
    layoutJSON = json.dumps(layout, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('graph.html',
                           graphJSON=graphJSON,
                           layoutJSON=layoutJSON)
