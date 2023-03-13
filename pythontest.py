import dash
from dash import dcc
from dash import html
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import schedule
import datetime
import time
import emoji
from dateutil.relativedelta import relativedelta
from datetime import timedelta

# Importer les données et mettre les prix en floatant
df = pd.read_csv('/home/ec2-user/projet_linux/tableur.csv', header=None, names=['date', 'prix'])
df['prix'] = df['prix'].apply(lambda x: float(x.replace(" ", "")))

# Temporalité (je l'ai enlevé de l'affichage car je n'ai pas réussi à le faire fonctionner)
granularity_options = [
    {'label': 'Journée', 'value': 'D'},
    {'label': 'Semaine', 'value': 'W'},
    {'label': 'Mois', 'value': 'M'}
]

# Fonction pour fixer la data en fonction de la temporalité (ne sers à rien du coup mais comme je voulais mettre une base de temps flexible, je m'en étais servi dès le début)
def filter_data(granularity):
    if granularity == 'D':
        return df
    elif granularity == 'W':
        return df.resample('W', on='date').last()
    elif granularity == 'M':
        return df.resample('M', on='date').last()

# VI & dataframe filtrée
initial_granularity = 'D'
filtered_data = filter_data(initial_granularity)

# Statistiques
# Stat sur tout le temps
# On veut la date sans le décalage car mon instance est en heure anglaise donc on rajoute une heure
last_date = filtered_data['date'].iloc[-1]
dt = datetime.datetime.strptime(last_date, '%Y-%m-%d %H:%M:%S') # même si notre date est dans le bon format, on est obligé de faire ça pour que ça marche
dt_plus_one_hour = dt + datetime.timedelta(hours=1)
last_date_plus_one_hour = dt_plus_one_hour.strftime('%Y-%m-%d %H:%M:%S')
# Le reste des statistiques
last_price = filtered_data['prix'].iloc[-1]
volatility = np.std(filtered_data['prix'])
highest_peak = max(filtered_data['prix'])
lowest_peak = min(filtered_data['prix'])
return_rate = ((last_price / filtered_data['prix'].iloc[0]) - 1) * 100

# Stat sur 24h (actualisé chaque jour à 20h)
df['date'] = pd.to_datetime(df['date'])
df['date'] = df['date'] + timedelta(hours=1)
# Avoir la data sur la journée précédente sur 24h
now = datetime.datetime.now()
last_20h = datetime.datetime(now.year, now.month, now.day+1, 20)
now = datetime.datetime.now()
if now.hour >= 20:
    last_20h = datetime.datetime(now.year, now.month, now.day, 20)
else:
    yesterday = now - datetime.timedelta(days=1)
    last_20h = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 20)
# Avoir la data sur la journée précédente sur 24h
start_time = last_20h - datetime.timedelta(hours=24)
end_time = last_20h
# Extraire les données des dernières 24 heures de 20h à 20h
data_last_24h = df[(df['date'] >= start_time) & (df['date'] < end_time)]
# Rendement
daily_return = ((data_last_24h['prix'].iloc[-1] / data_last_24h['prix'].iloc[0]) - 1) * 100
# Volatilité
last_24h_volatility = np.std(data_last_24h['prix'])
# Max et Min
highest_24h_peak = data_last_24h['prix'].max()
lowest_24h_peak = data_last_24h['prix'].min()
# Prix ouverture / cloture
ouverture = data_last_24h['prix'].iloc[0]
cloture = data_last_24h['prix'].iloc[-1]

# Exemple d'investissement d'un portefeuille de 1000$
portofolio = 1000
portofolio_daily = 1000 * (1 + daily_return /100)
portofolio_begin = 1000 * (1 + return_rate /100)

# Flèche pour variation (ne fonctionne pas non plus mais je le laisse au cas ou)
previous_price = filtered_data['prix'].iloc[-2]
arrow = html.I(className='fas fa-arrow-up') if last_price > previous_price else html.I(className='fas fa-arrow-down')

# Graphique initial
fig, ax = plt.subplots()
ax.plot(filtered_data['date'], filtered_data['prix'])

# titres et étiquettes d'axe
ax.set_title('Evolution du prix en fonction du temps')
ax.set_xlabel('Date')
ax.set_ylabel('Prix')

# Créer l'application Dash
app = dash.Dash(__name__)

# Ajouter le graphique et les valeurs à l'application
app.layout = html.Div(children=[
    html.Div(children=[
        html.H3(html.I('Projet Gabriel BAR'), style={'text-align': 'center', 'font-size': '2.5em', 'background-image': 'linear-gradient(to right, blue, red)', '-webkit-background-clip': 'text', 'color': 'transparent','text-decoration': 'underline'}),
	],
	style={
                'color': 'red',
                'background-color': 'white',
                'border': 'solid',
                'border-width': '2px',
                'border-color': 'black',
                'padding': '5px',
                'margin': '5px',
                'text-align': 'center',
            }
    ),
    dcc.Graph(
    id='graph',
    figure={
        'data': [
            {'x': filtered_data['date'], 'y': filtered_data['prix'], 'type': 'line', 'name': 'Prix', 'line': {'color': 'royalblue', 'width': 3}}
        ],
        'layout': {
            'title': {'text': 'Cours Ethereum', 'font': {'size': 32, 'family': 'Arial', 'color': 'black'}},
            'xaxis': {'title': 'Date (UTC)', 'showgrid': True, 'gridcolor': 'lightgray', 'tickformat': '%b %Y'},
            'yaxis': {'title': 'Prix (en USD)', 'showgrid': True, 'gridcolor': 'lightgray', 'tickprefix': '$'},
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white',
            'margin': {'l': 80, 'r': 50, 't': 100, 'b': 80}
        }
    }),
    html.Div(
    style={
        'display': 'flex',
        'flex-direction': 'column',
        'align-items': 'center'
    },
    children=[
	html.H3(html.I('Statistiques'), style={'font-size': '1.8em'}),
		html.Tr([
			html.Td([
				html.Strong(last_date_plus_one_hour.split()[0], style={'color': 'blue'}),
                		' ',
                		html.Strong(last_date_plus_one_hour.split()[1], style={'color': 'red'})
            ]),
        ]),
    ]),
    html.Div(
    children=[
	html.Table(
            [
             	html.Tr(
                    [
                     	html.Td(html.U(html.I('Dernier Prix'))),
                        html.Td('{:.2f}$'.format(last_price)),
                        arrow,
                    ]
                ),
                html.Tr([html.Td(html.U(html.I('Volatilité'))), html.Td('{:.2f}%'.format(volatility))]),
                html.Tr([html.Td(html.U(html.I('Rendement'))), html.Td('{:.2f}%'.format(return_rate))]),
                html.Tr([html.Td(html.U(html.I('Plus haut pic'))), html.Td('{:.2f}$'.format(highest_peak))]),
                html.Tr([html.Td(html.U(html.I('Plus bas pic'))), html.Td('{:.2f}$'.format(lowest_peak))]),
            ],
            style={
                'color': 'red',
                'background-color': 'white',
                'border': 'solid',
                'border-width': '2px',
                'border-color': 'black',
                'padding': '10px',
                'margin': '10px',
                'text-align': 'center',
            },
	),
    ],
    style={'display': 'flex', 'justify-content': 'center'}
    ),
    html.Div(
    children=[
	html.H3(html.I('Données journaliaires actualisées à 20h'), style={'font-size': '1em'}),
	html.Table(
            [
                html.Tr([html.Td(html.U(html.I('Rendement sur 24h'))), html.Td('{:.2f}%'.format(daily_return))]),
                html.Tr([html.Td(html.U(html.I('Volatilité sur 24h'))), html.Td('{:.2f}%'.format(last_24h_volatility))]),
		html.Tr([html.Td(html.U(html.I('Pic haut sur 24h'))), html.Td('{:.2f}$'.format(highest_24h_peak))]),
                html.Tr([html.Td(html.U(html.I('Pic bas sur 24h'))), html.Td('{:.2f}$'.format(lowest_24h_peak))]),
		html.Tr([html.Td(html.U(html.I('Ouverture'))), html.Td('{:.2f}$'.format(ouverture))]),
		html.Tr([html.Td(html.U(html.I('Cloture'))), html.Td('{:.2f}$'.format(cloture))]),
            ],
            style={
                'color': 'red',
                'background-color': 'white',
                'border': 'solid',
                'border-width': '2px',
                'border-color': 'black',
                'padding': '10px',
                'margin': '10px',
                'text-align': 'center',
            },
	),
    ],
    style={'display': 'flex', 'justify-content': 'center'}
    ),
    html.Div(
    style={
	'display': 'flex',
        'flex-direction': 'column',
        'align-items': 'center'
    },
    children=[
	html.H3(html.I('Exemple d investissement avec 1000$ journalier et 1000$ depuis le 6mars'), style={'font-size': '1em'}),
	]),
    html.Div(
    children=[
	html.Table(
            [
             	html.Tr([html.Td(html.U(html.I('Portefeuille'))), html.Td('{:.2f}$'.format(portofolio))]),
		html.Tr([html.Td(html.U(html.I('Portefeuille depuis 6mars'))), html.Td('{:.2f}$'.format(portofolio_begin))]),
                html.Tr([html.Td(html.U(html.I('Portefeuille journalier'))), html.Td('{:.2f}$'.format(portofolio_daily))]),
            ],
            style={
                'color': 'red',
                'background-color': 'white',
                'border': 'solid',
                'border-width': '2px',
                'border-color': 'black',
                'padding': '10px',
                'margin': '10px',
                'text-align': 'center',
            },
	),
    ],
    style={'display': 'flex', 'justify-content': 'center'}
    ),
])

# Lancer l'application
if __name__ == '__main__':
    app.run_server(host = '0.0.0.0',port = 8050, debug=True)

