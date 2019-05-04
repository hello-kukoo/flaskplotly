from flask import Flask, Response, make_response, render_template, request, redirect

import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from plotly import tools
import plotly_express as px

from dash import Dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc

import numpy as np
import pandas as pd
import urllib
import json
import math

from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css",
                    "https://unpkg.com/purecss@1.0.0/build/pure-min.css"]
server = Flask(__name__)
dash_app1 = Dash(__name__, server = server,
        url_base_pathname='/gapminder_app/',
        external_stylesheets=external_stylesheets)
dash_app2 = Dash(__name__, server = server,
        url_base_pathname='/tips_app/',
        external_stylesheets=external_stylesheets)


# Dash app1, the gapminder table and graph
df = px.data.gapminder()
bubble_size = [math.sqrt(p / math.pi) for p in df["pop"].values]
df['size'] = bubble_size
sizeref = 2*max(df['size'])/(100**2)
unique_continents = list(df["continent"].unique())

def _generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +
        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

dash_app1.layout = html.Div(
    children=[
        html.H4(children="预计寿命与GDP"),
        _generate_table(df),
        html.Br(),
        dcc.Dropdown(
            id="continent-dropdown",
            options=[
                {'label': i, 'value': i} for i in unique_continents
            ],
            value=unique_continents,
            multi=True
        ),
        dcc.Graph(id='graph-with-slider'),
        dcc.Slider(
            id='year-slider',
            min=df['year'].min(),
            max=df['year'].max(),
            value=df['year'].min(),
            step=None,
            marks={str(year): str(year) for year in df['year'].unique()}
        )
    ]
)

@dash_app1.callback(
    Output('graph-with-slider', 'figure'),
    [Input('year-slider', 'value'),
     Input('continent-dropdown', 'value')]
)
def update_gapminder_figure(selected_year, selected_continent):
    filtered_df = df[df.year == selected_year]
    filtered_df = filtered_df[df.continent.isin(selected_continent)]
    traces = []

    for i in filtered_df.continent.unique():
        df_by_continent = filtered_df[filtered_df['continent'] == i]
        traces.append(go.Scattergl(
            x=df_by_continent['gdpPercap'],
            y=df_by_continent['lifeExp'],
            text=df_by_continent['country'],
            mode='markers',
            opacity=0.7,
            marker={
                'size': df[df['continent'] == i]['size'],
                'line': {'width': 0.5, 'color': 'white'},
                'sizeref': sizeref,
                'symbol': 'circle',
                'sizemode': 'area'
            },
            name=i
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'type': 'log', 'title': 'GDP Per Capita'},
            yaxis={'title': 'Life Expectancy', 'range': [20, 90]},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest',
            template='ggplot2+presentation'
        )
    }


# Dash app2, Ployly Express in Dash with the tips dataset
tips = px.data.tips()
col_options = [dict(label=x, value=x) for x in tips.columns]
dimensions = ["x", "y", "color", "facet_col", "facet_row"]

dash_app2.layout = html.Div(
    [
        html.Div(
            [html.H2("Plotly/Dash Chart Demo")],
            style={
                "text-align": "center",
                "background-color": "rgb(136, 185, 229)",
                "height": "70px",
                "line-height": "70px"
            },
        ),
        html.H2("Demo: Plotly Express in Dash with Tips Dataset"),
        html.Div(
            [
                html.P([d + ":", dcc.Dropdown(id=d, options=col_options)])
                for d in dimensions
            ],
            style={"width": "25%", "float": "left"},
        ),
        dcc.Graph(id="graph", style={"width": "75%", "display": "inline-block"}),
    ]
)

@dash_app2.callback(
    Output("graph", "figure"),
    [Input(d, "value") for d in dimensions]
)
def update_tips_figure(x, y, color, facet_col, facet_row):
    fig = px.scatter(
        tips,
        x=x,
        y=y,
        color=color,
        facet_col=facet_col,
        facet_row=facet_row,
        height=700
    )
    fig.layout.template = 'seaborn+presentation'
    return fig


@server.route('/')
def index():
    return render_template('index.html')


def create_line():
    count = 500
    xScale = np.linspace(0, 100, count)
    yScale = np.random.randn(count)

    trace = go.Scattergl(x=xScale, y=yScale)
    figure = [trace]
    return figure


@server.route('/showLineChart')
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
    trace0 = go.Scattergl(
        x=xScale,
        y=y0_scale
    )
    trace1 = go.Scattergl(
        x=xScale,
        y=y1_scale
    )
    trace2 = go.Scattergl(
        x=xScale,
        y=y2_scale
    )
    figure = [trace0, trace1, trace2]
    return figure


@server.route('/showMultiChart')
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


@server.route('/plot3d')
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

@server.route('/plot3dcontours')
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


@server.route('/sankey')
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
    trace1 = go.Scattergl(
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

@server.route('/barandline')
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

@server.route('/sunburst')
def sunburst():
    figure, layout = create_sunburst()
    graphJSON = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
    layoutJSON = json.dumps(layout, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('graph.html',
                           graphJSON=graphJSON,
                           layoutJSON=layoutJSON)


# Import dataset
data = pd.read_csv('data/gapminder.csv')
data = data[(data.Year >= 1950)]
country_names = sorted(list(set(data.Country)))
attribute_names = data.columns[2:-1].values.tolist()

# Create the main plot
def create_gapminder_figure(first_country='China',
                  second_country='Singapore',
                  selected_attribute='income'):

    # filter datasets according to country
    first_country_data = data[(data.Country == first_country)]
    second_country_data = data[(data.Country == second_country)]

    first_country_data_attribute = list(first_country_data[selected_attribute])
    second_country_data_attribute = list(second_country_data[selected_attribute])

    years = list(first_country_data["Year"])

    # Create traces
    trace0 = go.Scattergl(
        x = years,
        y = first_country_data_attribute,
        mode = 'lines',
        name = first_country
    )
    trace1 = go.Scattergl(
        x = years,
        y = second_country_data_attribute,
        mode = 'lines',
        name = second_country
    )
    figure = [trace0, trace1]

    layout = go.Layout(
        title="Gapminder",
        width=1500,
        height=700,
    )

    return figure, layout


@server.route('/gapminder', methods=['GET', 'POST'])
def gapminder_plot():
    first_country = "China"
    second_country = "Singapore"
    selected_attribute = "income"
    if request.method == 'POST':
        first_country = request.form["first_country"]
        second_country = request.form["second_country"]
        selected_attribute = request.form["selected_attribute"]

    # Create the plot
    figure, layout = create_gapminder_figure(first_country, second_country, selected_attribute)
    graphJSON = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
    layoutJSON = json.dumps(layout, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("gapminder.html",
                           graphJSON=graphJSON,
                           layoutJSON=layoutJSON,
                           country_names=country_names,
                           attribute_names=attribute_names,
                           selected_attribute=selected_attribute,
                           first_country=first_country,
                           second_country=second_country)


def create_animated_scatter():
    fig = px.scatter(df, x="gdpPercap", y="lifeExp", animation_frame="year", animation_group="country",
           size="pop", color="continent", hover_name="country", facet_col="continent",
           log_x=True, size_max=45, range_x=[100,100000], range_y=[25,90])

    return fig.data, fig.layout

@server.route('/scatter_animation')
def scatter_animation():
    figure, layout = create_animated_scatter()
    graphJSON = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
    layoutJSON = json.dumps(layout, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("graph.html",
                           graphJSON=graphJSON,
                           layoutJSON=layoutJSON)


@server.route('/gapminder_app')
def render_dashboard():
    return redirect('/dash_gapminder')


@server.route('/tips_app')
def render_reports():
    return redirect('/dash_tips')


app = DispatcherMiddleware(server, {
    '/dash_gapminder': dash_app1.server,
    '/dash_tips': dash_app2.server
})

if __name__ == '__main__':
    run_simple('127.0.0.1', 8080, app, use_reloader=True, use_debugger=True)
