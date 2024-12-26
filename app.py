import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go

# Функция для загрузки данных
def load_data():
    data = pd.read_csv('Data_test.csv', encoding='utf-8', sep=";")
    # Убираем пропуски в ключевых столбцах
    data = data.dropna(subset=['Name', 'KolPlanYear', 'KolFaktVs', 'KolPlanM', 'KolFaktM', 'M', 'Graphic'])
    return data

# Список названий месяцев
MONTHS = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
]


# Инициализация приложения
app = Dash(__name__)
app.title = "Информационная панель"

# Загрузка данных
data = load_data()

# Layout приложения
app.layout = html.Div([
    html.H1("Информационная панель"),
    html.H2("Производство"),
    
    # Фильтр по номеру графика
    html.Div([
        dcc.Dropdown(
        id='graphic-dropdown',
        options=[{'label': f'Выполнение плана по изделию {str(g)}', 'value': g} for g in data['Graphic'].unique()],
        placeholder="Выберите номер графика",
        clearable=True
    ),
    
    # Фильтр по месяцу
    dcc.Dropdown(
        id='month-dropdown',
        options=[
            {'label': MONTHS[i - 1], 'value': i} for i in range(1, 13)
        ],
        value=9,  # Установка месяца "Сентябрь" по умолчанию
        clearable=False
    ),
], style={'display': 'flex', 'flex-direction': 'column', 'gap': '20px'}),

    
    dcc.Graph(id='data-graph')
])

# Callback для обновления графиков
@app.callback(
    Output('data-graph', 'figure'),
    [Input('graphic-dropdown', 'value'),
     Input('month-dropdown', 'value')]
)
def update_graph(selected_graphic, selected_month):
    # Фильтрация данных
    filtered_data = data[data['M'] == selected_month]
    if selected_graphic:
        filtered_data = filtered_data[filtered_data['Graphic'] == selected_graphic]
    
    # Проверка на пустую таблицу
    if filtered_data.empty:
        return {
            'data': [],
            'layout': {'title': 'Нет данных для отображения'}
        }
    
    # Построение графика с использованием plotly.graph_objects
    figure = go.Figure()

    # Годовой план
    figure.add_trace(go.Bar(
        x=filtered_data['Name'],
        y=filtered_data['KolPlanYear'],
        name="Годовой план",
        marker_color='rgba(200, 200, 200, 0.8)'
    ))

    # Факт накопительным итогом
    figure.add_trace(go.Bar(
        x=filtered_data['Name'],
        y=filtered_data['KolFaktVs'],
        name="Факт накопительным итогом",
        marker_color='rgba(100, 200, 100, 0.8)'
    ))

    # План за месяц
    figure.add_trace(go.Bar(
        x=filtered_data['Name'],
        y=filtered_data['KolPlanM'],
        name="План за месяц",
        marker_color='rgba(100, 150, 250, 0.8)'
    ))

    # Факт за месяц
    figure.add_trace(go.Bar(
        x=filtered_data['Name'],
        y=filtered_data['KolFaktM'],
        name="Факт за месяц",
        marker_color='rgba(250, 150, 100, 0.8)'
    ))

    # Настройки оформления графика
    figure.update_layout(
        title=f'Данные за {MONTHS[selected_month - 1]}',
        barmode='group',
        xaxis_title='Изделие',
        yaxis_title='Значение',
        paper_bgcolor='rgba(255,255,255,1)',
        plot_bgcolor='rgba(240,240,240,1)'
    )

    return figure

# Запуск приложения
if __name__ == '__main__':
    app.run_server(debug=True)