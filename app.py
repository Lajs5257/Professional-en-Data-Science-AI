from jupyter_dash import JupyterDash # Versión de dash para notebooks
from dash import dcc # Componentes HTML preconstruidos para dashboards
from dash import html # Componentes HTML nativos
from dash.dependencies import Input, Output # Clases Input y Output
import plotly.express as px # Generar gráficas e importar datasets con Plotly

import pandas as pd # Recolección y manipulación de datos
from dash import Dash
import plotly.graph_objects as go
import requests
import zipfile

with zipfile.ZipFile('./denue_00_31-33_1121_csv.zip', 'r') as zip_ref:
    zip_ref.extractall('./')
repo_url = 'https://raw.githubusercontent.com/angelnmara/geojson/master/mexicoHigh.json' 
#Archivo GeoJSON
mx_regions_geo = requests.get(repo_url).json()


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)


# cargamos nuestro conjunto de datos
dfDatos = pd.read_csv('./conjunto_de_datos/denue_inegi_31-33_.csv', encoding="ISO-8859-1",dtype={'telefono': 'string'})
# ahora convertimos la columna fecha_alta a tipo fecha en años para facilitar el filtrado
dfDatos['fecha_alta'] = pd.to_datetime(dfDatos['fecha_alta'].astype(str), format='%Y-%m')
dfDatos['fecha_alta'] = pd.DatetimeIndex(dfDatos['fecha_alta']).year

# ahora filtramos el conjunto de datos para obtener todos años
lista_year = dfDatos.sort_values("fecha_alta")["fecha_alta"].unique()
data_year=pd.DataFrame(lista_year, columns=['fecha_alta'])

# ahora filtramos el conjunto de datos para obtener todos los estados
dfEmpresasEstadosAnios=dfDatos[['entidad','fecha_alta','id']].groupby(['entidad','fecha_alta']).count().reset_index()
dfEmpresasAnios = dfDatos[['fecha_alta','id']].groupby(['fecha_alta']).count().reset_index()
# empresas creadas por año
fig2 = px.bar(dfEmpresasAnios, x="fecha_alta", y="id", title="Empresas por año")

fig3 = px.line(dfEmpresasEstadosAnios, x="fecha_alta", y="id", color='entidad', title="Empresas por año y estado")

# creamos nuestro dashboard
app.layout = html.Div([
    html.H1("Industrias manufactureras"),
    html.P("Desde julio de 2010 el Instituto Nacional de Estadística y Geografía ha puesto a disposición de la sociedad el Directorio Estadístico Nacional de Unidades Económicas (DENUE) con in- formación de los negocios activos del país. Los datos que propor- ciona el DENUE permiten identificar a las unidades económicas por el nombre comercial, el tipo de organización jurídica (personas físicas o morales), por su actividad económica y por su tamaño (con base en el estrato de personal ocupado); así como, ubicarlas en el territorio mexicano por regiones, localidades, manzanas y calles. El Directorio también provee las coordenadas geográficas de la ubicación de los establecimientos para que puedan ser visualizados en la cartografía digital o en imágenes satelitales."),
    html.H2("¿Por qué se eligió este conjunto de datos?"),
    html.P("El conjunto de datos que se eligió para este proyecto es el de las industrias manufactureras, ya que es un sector que ha crecido en los últimos años y que ha generado muchos empleos en el país, por lo que es importante conocer el comportamiento de este sector en el país."),
    html.P("Así mismo, el poder ver como esta pandemia afecto en la creación de nuevas empresas en el país, ya que se puede ver que en el año 2020 hubo una disminución en la creación de nuevas empresas, lo que puede ser un indicador de que la pandemia afecto a este sector."),
    html.H2("¿Comó se comporto la creación de nuevas empresas en el país por año?"),
    dcc.Graph(figure=fig2),
    html.H2("¿Comó se comporto la creación de nuevas empresas en el país por año y por estado?"),
    html.Div([
        html.Label("Año"),
        dcc.Dropdown(data_year['fecha_alta'], id='year', placeholder='Selecciona un año',value=2010),
    ]),
    dcc.Graph(id="graph"),
    dcc.Graph(figure=fig3),
    
])


@app.callback(
    Output("graph", "figure"),
    Input("year", "value"))
    
def update_figure(year):    
    dfEEA=dfEmpresasEstadosAnios.query(f'fecha_alta == {year}')
    fig = px.choropleth(data_frame=dfEEA, 
                        geojson=mx_regions_geo, 
                        locations=dfEEA['entidad'], # nombre de la columna del Dataframe
                        featureidkey='properties.name',  # ruta al campo del archivo GeoJSON con el que se hará la relación (nombre de los estados)
                        color=dfEEA['id'], #El color depende de las cantidades
                        color_continuous_scale="burg",
                        scope="north america"
                    )

    fig.update_geos(showcountries=True, showcoastlines=True, showland=True, fitbounds="locations")
    return fig

if __name__ == '__main__':
    app.run_server(debug=False)