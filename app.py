import pandas as pd
from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import plotly.graph_objects as go


ARQUIVO_CSV   = 'dialise_fav_final3.csv'
SEPARADOR_CSV = ';'

paleta = {
    'principal'   : '#0077B6',
    'secundario'  : '#90E0EF',
    'terceario'   : '#48CAE4',
    'quarto'      : '#023E8A',
    'quinto'      : '#F8F9FA',
    'texto'       : '#6C757D',
    'fundo'       : '#FFFFFF'
}

PORTA_HTTP = 8080

if __name__ == '__main__':
    df = pd.read_csv(ARQUIVO_CSV, sep=SEPARADOR_CSV)
    df.sample(5)

    # Mantém só POA. Deve ser o primeiro passo a ser rodado
    df = df[df['AP_UFMUN'] == 431490]
    df.drop(columns=['AP_UFMUN', 'AP_UFDIF', 'AP_UFNACIO', 'fav_AP_UFMUN', 'fav_AP_UFDIF', 'fav_AP_UFNACIO'])

    df_espera = pd.DataFrame()

    # Pergunta 1 e 2
    df_espera['data_primeira_dialise']      = df['ATD_DTPDR']
    df_espera['cronico']                    = df['Cronico']
    df_espera['data_atendimento_dialitico'] = df['AP_CMP']
    df_espera['obito']                      = df['AP_OBITO']
    df_espera['data_atendimento_fav']       = df['fav_AP_CMP']
    df_espera.sample(10)

    # Pergunta 3
    df_espera['genero'] = df['AP_SEXO']
    df_espera['idade'] = df['AP_NUIDADE']

    # Pergunta 4
    df_espera['hospital'] = df['fav_AP_CODUNI']

    # Para os casos de morte, podemos desconsiderar o tempo de espera (?)
    df_espera_mortos_validos = df_espera[df_espera.obito == 1][df_espera.data_atendimento_fav.notna()]

    # Remover todos os mortos
    df_espera = df_espera[df_espera.obito != 1]

    # Inserir apenas falecidos válidos
    df_espera = pd.concat([df_espera, df_espera_mortos_validos])
    df_espera.sample(10)

    # Priorizar remover repetidos NaN
    df_espera = df_espera[df_espera.cronico != 'repetido']
    df_espera.sample(5)

    # Remover observações que não são agudos e que não tiveram atendimento FAV
    # Para garantir, vamos remover todos que não tiveram data_primeira_dialise também
    df_espera = df_espera[df_espera.cronico != 'agudo']
    df_espera = df_espera[df_espera.data_atendimento_fav.notna()]
    df_espera = df_espera[df_espera.data_primeira_dialise.notna()]
    df_espera.sample(10)

    # Calcular tempo de espera
    df_espera['data_atendimento_fav'] = pd.to_datetime(df_espera['data_atendimento_fav'])
    df_espera['data_primeira_dialise'] = pd.to_datetime(df_espera['data_primeira_dialise'])

    # Calcular a diferença
    df_espera['tempo_entre_fav_e_primeira_dialise'] = (
        df_espera['data_atendimento_fav'] - df_espera['data_primeira_dialise']
    ).dt.days  # em dias

    df_espera['tempo_anos'] = df_espera['tempo_entre_fav_e_primeira_dialise'] / 365.25

    # Remover esperas negativas
    df_espera = df_espera[df_espera['tempo_entre_fav_e_primeira_dialise'] > 0]
    df_espera.sample(10)

    # Manter dados apenas a partir de janeiro de 2014 devido criação do dataset
    df_espera['data_atendimento_dialitico'] = pd.to_datetime(df_espera['data_atendimento_dialitico'])
    df_espera['data_atendimento_fav'] = pd.to_datetime(df_espera['data_atendimento_fav'])
    df_espera['data_primeira_dialise'] = pd.to_datetime(df_espera['data_primeira_dialise'])

    df_espera = df_espera[
            (df_espera['data_atendimento_dialitico'] >= '2014-01-01') &
            (df_espera['data_atendimento_fav'] >= '2014-01-01') &
            (df_espera['data_primeira_dialise'] >= '2014-01-01') ]

    df_perfil = df_espera[(df_espera.genero.notna()) & (df_espera.idade.notna())]

    df_perfil['perfil_paciente'] = pd.cut(
        df_perfil['idade'],
        bins=[0, 18, 40, 60, 150],
        labels=['Jovem', 'Adulto Jovem', 'Meia Idade', 'Idoso']
    )
    df_perfil['ano_primeira_dialise'] = pd.to_datetime(df_perfil['data_primeira_dialise']).dt.year

    df_hospital = df_espera[df_espera.hospital.notna()]
    df_hospital.sample()
    df_hospital['hospital'] = df_hospital['hospital'].astype(str)

    df_hospital['ano_primeira_dialise'] = pd.to_datetime(df_hospital['data_primeira_dialise']).dt.year
    # Criar coluna de ano
    df_hospital['ano_primeira_dialise'] = pd.to_datetime(df_hospital['data_primeira_dialise']).dt.year

    # Gráfico de tempo de espera
    max_tempo = df_espera['tempo_entre_fav_e_primeira_dialise'].max()
    bins = list(range(0, int(max_tempo) + 10, 10))

    # Plotar histograma
    fig1_p1 = px.histogram(
        df_espera,
        x='tempo_entre_fav_e_primeira_dialise',
        nbins=len(bins),
        title='Distribuição do Tempo de Espera para Atendimento no FAV',
        labels={
            'tempo_entre_fav_e_primeira_dialise': 'Tempo de espera (dias)',
            'count': 'Quantidade de pessoas'
        },
        color_discrete_sequence=[paleta['principal']]  # Cor das barras
    )

    # Layout personalizado com a paleta
    fig1_p1.update_layout(
        xaxis_title='Tempo de espera (dias)',
        yaxis_title='Quantidade de pessoas',
        bargap=0.05,
        template='plotly_white',
        plot_bgcolor=paleta['fundo'],
        paper_bgcolor=paleta['fundo'],
        font=dict(color=paleta['quarto']),
        title_font=dict(size=18, color=paleta['quarto']),
        xaxis=dict(
            gridcolor=paleta['quinto'],
            linecolor=paleta['texto'],
            tickfont=dict(color=paleta['quarto'])
        ),
        yaxis=dict(
            gridcolor=paleta['quinto'],
            linecolor=paleta['texto'],
            tickfont=dict(color=paleta['quarto'])
        )
    )

    df_espera['ano_primeira_dialise'] = df_espera['data_primeira_dialise'].dt.year
    df_agrupado = df_espera.groupby('ano_primeira_dialise')['tempo_entre_fav_e_primeira_dialise'].mean().reset_index()

    fig2_p1 = px.bar(
        df_agrupado,
        x='ano_primeira_dialise',
        y='tempo_entre_fav_e_primeira_dialise',
        text='tempo_entre_fav_e_primeira_dialise',
        labels={
            'ano_primeira_dialise': 'Ano da Primeira Diálise',
            'tempo_entre_fav_e_primeira_dialise': 'Tempo médio de espera (dias)'
        },
        title='Tempo Médio de Espera por Ano da Primeira Diálise até a FAV',
        color='tempo_entre_fav_e_primeira_dialise',
        color_continuous_scale='Blues'
    )

    # Personalizar layout
    fig2_p1.update_traces(texttemplate='%{text:.0f} dias', textposition='outside')

    fig2_p1.update_layout(
        xaxis=dict(tickmode='linear'),
        yaxis_title='Tempo médio de espera (dias)',
        xaxis_title='Ano da primeira diálise',
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        plot_bgcolor='white',
        width=900,
        height=500
    )

    # Garantir que a coluna data_primeira_dialise está em datetime
    df_espera['data_primeira_dialise'] = pd.to_datetime(df_espera['data_primeira_dialise'])

    # Criar coluna de ano-mês
    df_espera['ano_mes'] = df_espera['data_primeira_dialise'].dt.to_period('M').astype(str)

    # Agrupar por ano-mês
    df_mes = df_espera.groupby('ano_mes')['tempo_entre_fav_e_primeira_dialise'].mean().reset_index()

    # Converter ano-mês para datetime (para plotar no eixo)
    df_mes['ano_mes_dt'] = pd.to_datetime(df_mes['ano_mes'])

    # Gráfico de Linha (sem pontos)
    fig1_p2 = go.Figure()

    fig1_p2.add_trace(go.Scatter(
        x=df_mes['ano_mes_dt'],
        y=df_mes['tempo_entre_fav_e_primeira_dialise'],
        mode='lines',
        name='Tempo médio de espera',
        line=dict(color=paleta['principal'], width=3)
    ))

    # Tarja vermelha para COVID-19 (março de 2020 até dezembro de 2021)
    fig1_p2.add_vrect(
        x0="2020-03-01", x1="2021-12-31",
        fillcolor="red", opacity=0.2,
        layer="below", line_width=0,
        annotation_text="COVID-19", annotation_position="top left",
        annotation_font_size=12, annotation_font_color="red"
    )

    # Layout final com paleta aplicada
    fig1_p2.update_layout(
        title='Média do Tempo de Espera por Mês',
        xaxis_title='Ano',
        yaxis_title='Tempo médio de espera (dias)',
        template='plotly_white',
        plot_bgcolor=paleta['fundo'],
        paper_bgcolor=paleta['fundo'],
        font=dict(color=paleta['quarto']),
        title_font=dict(size=18, color=paleta['quarto']),
        width=1000,
        height=500,
        xaxis=dict(
            tickformat='%Y',
            dtick="M12",
            showgrid=True,
            gridcolor=paleta['quinto'],
            linecolor=paleta['texto'],
            tickfont=dict(color=paleta['quarto'])
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=paleta['quinto'],
            linecolor=paleta['texto'],
            tickfont=dict(color=paleta['quarto'])
        )
    )
    # Preparar dados
    df_evolucao = df_espera.groupby("ano_primeira_dialise")['tempo_entre_fav_e_primeira_dialise'].mean().reset_index()

    # Criar o gráfico com melhorias
    fig2_p2 = px.line(
        df_evolucao,
        x="ano_primeira_dialise",
        y="tempo_entre_fav_e_primeira_dialise",
        markers=True,
        title="Evolução do Tempo Médio de Espera entre FAV e Primeira Diálise"
    )

    # Melhorias visuais
    fig2_p2.update_traces(line=dict(width=3), marker=dict(size=8))

    fig2_p2.update_layout(
        title={
            'text': 'Evolução do Tempo Médio de Espera entre FAV e Primeira Diálise',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title="Ano da Primeira Diálise",
        yaxis_title="Tempo Médio de Espera (dias)",
        font=dict(
            family="Arial, sans-serif",
            size=14,
            color="#333333"
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(
            showline=True,
            linewidth=1,
            linecolor='black',
            gridcolor='lightgrey',
            tickmode='linear'
        ),
        yaxis=dict(
            showline=True,
            linewidth=1,
            linecolor='black',
            gridcolor='lightgrey'
        ),
        hovermode="x unified"
    )

    genero_cores = {
        'F': paleta['quarto'],
        'M': paleta['secundario']
    }

    fig1_p3 = px.scatter(
        df_perfil,
        x='idade',
        y='tempo_entre_fav_e_primeira_dialise',
        color='genero',
        labels={
            'idade': 'Idade',
            'tempo_entre_fav_e_primeira_dialise': 'Tempo de espera (dias)',
            'genero': 'Gênero'
        },
        title='Perfil dos Pacientes vs Tempo de Espera para Confecção da FAV',
        color_discrete_map=genero_cores
    )

    # Layout com paleta médica
    fig1_p3.update_layout(
        plot_bgcolor=paleta['fundo'],
        paper_bgcolor=paleta['fundo'],
        font=dict(color=paleta['quarto']),
        title_font=dict(size=18, color=paleta['quarto']),
        xaxis=dict(
            title='Idade',
            gridcolor=paleta['quinto'],
            linecolor=paleta['texto']
        ),
        yaxis=dict(
            title='Tempo de espera (dias)',
            gridcolor=paleta['quinto'],
            linecolor=paleta['texto']
        )
    )
    # Agrupar dados por perfil e gênero
    df_perfil_group = (
        df_perfil.groupby(['perfil_paciente', 'genero'])['tempo_entre_fav_e_primeira_dialise']
        .mean()
        .reset_index()
    )

    # Criar o gráfico de barras empilhadas
    fig2_p3 = px.bar(
        df_perfil_group,
        x="perfil_paciente",
        y="tempo_entre_fav_e_primeira_dialise",
        color="genero",
        color_discrete_map=genero_cores,
        barmode="stack",
        text_auto=".1f",
        title="Tempo Médio de Espera entre FAV e Primeira Diálise por Perfil de Paciente e Gênero"
    )

    # Melhorias visuais e layout
    fig2_p3.update_layout(
        title={
            'text': 'Tempo Médio de Espera por Perfil de Paciente e Gênero',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title="Perfil do Paciente",
        yaxis_title="Tempo Médio de Espera (dias)",
        font=dict(
            family="Arial, sans-serif",
            size=14,
            color=paleta['texto']
        ),
        plot_bgcolor=paleta['fundo'],
        paper_bgcolor=paleta['fundo'],
        xaxis=dict(
            showline=True,
            linewidth=1,
            linecolor='black',
            gridcolor='lightgrey'
        ),
        yaxis=dict(
            showline=True,
            linewidth=1,
            linecolor='black',
            gridcolor='lightgrey'
        ),
        legend_title_text='Gênero',
        bargap=0.15
    )

    # Ajuste de rótulos nas barras
    fig2_p3.update_traces(textposition='outside')


    df_espera['hospital'] = df_espera['hospital'].astype(str)

    top_25_maiores = df_espera.sort_values(by='tempo_entre_fav_e_primeira_dialise', ascending=False).head(25)

    top_25_menores = df_espera.sort_values(by='tempo_entre_fav_e_primeira_dialise', ascending=True).head(25)

    df_extremos = pd.concat([top_25_maiores, top_25_menores]).reset_index(drop=True)
    df_extremos[['hospital', 'idade', 'genero', 'tempo_entre_fav_e_primeira_dialise', 'data_primeira_dialise', 'data_atendimento_fav']]
    df_extremos.sample(5)

    # Agrupar por hospital e ano
    df_heat = df_hospital.groupby(['hospital', 'ano_primeira_dialise'])['tempo_entre_fav_e_primeira_dialise'].mean().reset_index()

    # Pivotar para criar matriz do heatmap
    heatmap_data = df_heat.pivot(
        index='hospital',
        columns='ano_primeira_dialise',
        values='tempo_entre_fav_e_primeira_dialise'
    )

    # 🔵 Substituir NaNs por -1 (para representar ausência de dados no heatmap)
    z_data = heatmap_data.fillna(-1).values

    # 🔵 Criar texto do hover personalizado
    hover_text = []
    for i, hospital in enumerate(heatmap_data.index):
        row = []
        for j, ano in enumerate(heatmap_data.columns):
            valor = z_data[i][j]
            if valor == -1:
                row.append(
                    f"Hospital: {hospital}<br>Ano: {ano}<br><b>Sem informação</b>"
                )
            else:
                row.append(
                    f"Hospital: {hospital}<br>Ano: {ano}<br>Tempo médio: {valor:.0f} dias"
                )
        hover_text.append(row)

    # 🔵 Definir uma escala de cores personalizada com preto para NaN (-1)
    colorscale = [
        [0.0, 'rgb(99,99,99)'],                           # NaN → preto
        [0.00001, 'rgb(239,243,255)'],             # início da paleta Blues
        [0.2, 'rgb(189,215,231)'],
        [0.4, 'rgb(107,174,214)'],
        [0.6, 'rgb(33,113,181)'],
        [1.0, 'rgb(8,48,107)']                     # fim da paleta Blues
    ]

    # 🔵 Construir o Heatmap
    fig1_p4 = go.Figure(
        data=go.Heatmap(
            z=z_data,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            text=hover_text,
            hoverinfo='text',
            colorscale=colorscale,
            colorbar=dict(title='Tempo médio (dias)'),
            zmin=heatmap_data.min().min(),
            zmax=heatmap_data.max().max(),
            hoverongaps=False
        )
    )

    # 🔵 Layout
    fig1_p4.update_layout(
        title='Tempo Médio de Espera para FAV - Hospital x Ano',
        xaxis_title='Ano da Primeira Diálise',
        yaxis_title='Hospital',
        xaxis=dict(side='bottom'),
        yaxis=dict(autorange="reversed"),
        plot_bgcolor=paleta['fundo'],
        paper_bgcolor=paleta['fundo'],
        font=dict(color=paleta['quarto']),
        title_font=dict(size=18, color=paleta['quarto']),
    )


    NOMES = 'Gabriela Dellamora, Luciano da Rocha, Nícolas Moraes, Tiago Gambogi'

    app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
    app.title = "Dashboard FAV"

    def gerar_card(titulo, grafico):
        return dbc.Card(
            [
                dbc.CardHeader(html.H5(titulo, className="text-center fw-bold")),
                dbc.CardBody(
                    dcc.Graph(figure=grafico, config={'displayModeBar': False}),
                    style={"height": "100%"}
                )
            ],
            className="shadow-sm mb-4 h-100"
        )

    def gerar_kpi(titulo, valor, cor="primary"):
        return dbc.Card(
            dbc.CardBody([
                html.H6(titulo, className="card-title"),
                html.H4(valor, className="card-text fw-bold")
            ]),
            color=cor, inverse=True, className="shadow-sm mb-4"
        )

    # Layout do App
    app.layout = dbc.Container([

        # Header
        dbc.Row([
            dbc.Col(html.H1(
                "Dashboard - Tempo de Espera na FAV",
                className="text-center text-primary my-4"
            ))
        ]),
        dbc.Row([
            dbc.Col(html.H5(
                "Análise dos tempos de espera entre a primeira diálise e o atendimento na FAV.",
                className="text-center text-secondary mb-4"
            ))
        ]),

        # KPIs
        dbc.Row([
            dbc.Col(gerar_kpi("Tempo Médio de Espera", f"{round(df_espera['tempo_entre_fav_e_primeira_dialise'].mean(), 1)} dias", "primary"), width=3),
            dbc.Col(gerar_kpi("Total de Hospitais", df_espera['hospital'].nunique(), "info"), width=3),
            dbc.Col(gerar_kpi("Total de Pacientes", df_espera.shape[0], "success"), width=3),
            dbc.Col(gerar_kpi("Período da Base", f"{df_espera['ano_primeira_dialise'].min()} - {df_espera['ano_primeira_dialise'].max()}", "warning"), width=3),
        ], class_name="mb-4"),

        # Janelas
        dbc.Tabs([

            # Visão Geral
            dbc.Tab(label="Visão Geral", tab_id="tab-geral", children=[
                dbc.Row([
                    dbc.Col(gerar_card("Distribuição do Tempo de Espera", fig1_p1), width=6),
                    dbc.Col(gerar_card("Tempo Médio por Ano", fig2_p1), width=6),
                ]),
            ]),

            # Análises Detalhadas
            dbc.Tab(label="Análises Detalhadas", tab_id="tab-detalhes", children=[
                dbc.Row([
                    dbc.Col(gerar_card("Dispersão: Idade x Tempo de Espera", fig1_p3), width=6),
                    dbc.Col(gerar_card("Tempo Médio por Perfil e Gênero", fig2_p3), width=6),
                ]),
            ]),

            # Evolução
            dbc.Tab(label="Evolução do Tempo de Espera", tab_id="tab-evolucao", children=[
                dbc.Row([
                    dbc.Col(gerar_card("Evolução Mensal com COVID", fig1_p2), width=12),
                ]),
                dbc.Row([
                    dbc.Col(gerar_card("Evolução Anual", fig2_p2), width=12),
                ]),
            ]),

            # Análise Hospital/Ano
            dbc.Tab(label="Hospital x Ano", tab_id="tab-hospital", children=[
                dbc.Row([
                    dbc.Col(gerar_card("Tempo Médio - Heatmap Hospital x Ano", fig1_p4), width=12),
                ])
            ]),

            # Dados Tabulares
            dbc.Tab(label="Base de Dados", tab_id="tab-dados", children=[
                dbc.Row([
                    dbc.Col(html.H5(
                        "Base de dados consolidada utilizada nesta análise:",
                        className="text-center text-secondary my-3"
                    ), width=12)
                ]),
                dbc.Row([
                    dbc.Col(dash_table.DataTable(
                        data=df_espera.to_dict('records'),
                        columns=[{"name": i, "id": i} for i in df_espera.columns],
                        page_size=20,
                        style_table={'overflowX': 'auto'},
                        style_header={
                            'backgroundColor': 'rgb(230, 230, 230)',
                            'fontWeight': 'bold',
                            'textAlign': 'center'
                        },
                        style_cell={
                            'textAlign': 'center',
                            'padding': '5px',
                            'minWidth': '100px', 'width': '100px', 'maxWidth': '180px',
                            'whiteSpace': 'normal',
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(248, 248, 248)'
                            }
                        ],
                        filter_action="native",
                        sort_action="native",
                        sort_mode="multi",
                        column_selectable="single",
                        selected_columns=[],
                        selected_rows=[],
                        page_action="native",
                    ), width=12)
                ])
            ]),

        ], id="tabs", active_tab="tab-geral", class_name="mb-4"),

        # Footer
        dbc.Row([
            dbc.Col(html.Hr())
        ]),
        dbc.Row([
            dbc.Col(html.P(
                f"Dashboard desenvolvido por {NOMES} • Dados atualizados automaticamente • Versão 1.0",
                className="text-center text-muted"
            ))
        ])

    ], fluid=True)

    app.run(debug=True, port=PORTA_HTTP)