import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import requests
import plotly.figure_factory as ff
import plotly.express as px
import pickle
from streamlit_option_menu import option_menu


import warnings
warnings.filterwarnings('ignore')
warnings.filterwarnings('default')

model = pickle.load(open('data/modelo_churn_regressao_logistica.pkl', 'rb'))

# Carregar o DataFrame
@st.cache_data
def load_data():
    # verifica o diretório atual
    cwd = os.getcwd()
    # monta o caminho incluindo o nome do dataframe
    path = os.path.join(cwd, 'data/data-test-analytics.csv')
    # cria o dataframe
    df = pd.read_csv(path)

    # Delete nas colunas que não serão usadas
    df.drop(columns=['name_hash', 'email_hash', 'address_hash'], inplace= True, axis=1)

    # Convertendo colunas (assuming 'created_at', 'updated_at', 'deleted_at', 'last_date_purchase', and 'birth_date')
    for col in ['created_at', 'updated_at', 'deleted_at', 'last_date_purchase', 'birth_date']:
        df[col] = pd.to_datetime(df[col])

    # Corrigindo formatação das colunas de endereço pois foi encontrado espaço em branco
    for col in ['state', 'city', 'neighborhood']:
        df[col] =  df[col].str.strip()

    return df

def plot_cancelations_by_period(df, period):
    # Remover as entradas 'Ativa'
    df_filtered = df[df['deleted_at'] != 'Ativa']

    # Converter a coluna 'deleted_at' para o formato de data e hora
    df_filtered['deleted_at'] = pd.to_datetime(df_filtered['deleted_at'])

    # Criar a coluna 'periodo' de acordo com a periodicidade especificada
    if period == 'A':
        df_filtered['periodo'] = df_filtered['deleted_at'].dt.strftime('%Y')
        title = 'Ano'
    elif period == 'M':
        df_filtered['periodo'] = df_filtered['deleted_at'].dt.strftime('%Y-%m')
        title = 'Mês'
    elif period == 'T':
        df_filtered['periodo'] = df_filtered['deleted_at'].dt.to_period('Q').astype(str)
        title = 'Trimestre'
    else:
        st.error("Período inválido. Escolha entre 'A' (Anual), 'M' (Mensal) ou 'T' (Trimestral).")
        return

    # Agrupar por 'periodo' e contar o número de cancelamentos
    cancelations_by_period = df_filtered.groupby('periodo').size().reset_index(name='cancelations')

    # Plotar o gráfico de séries temporais
    st.subheader(f'Quantidade de assinaturas canceladas por {title}')
    st.line_chart(cancelations_by_period.set_index('periodo'))

def plot_revenue_by_period(df, period):
    # Converter a coluna 'created_at' para o formato de data e hora
    df['created_at'] = pd.to_datetime(df['created_at'])

    # Criar a coluna 'periodo' de acordo com a periodicidade especificada
    if period == 'A':
        df['periodo'] = df['created_at'].dt.strftime('%Y')
        title = 'Ano'
    elif period == 'M':
        df['periodo'] = df['created_at'].dt.strftime('%Y-%m')
        title = 'Mês'
    else:
        st.error("Período inválido. Escolha entre 'A' (Anual) ou 'M' (Mensal).")
        return

    # Agrupar por 'periodo' e somar a receita total
    revenue_by_period = df.groupby('periodo')['all_revenue'].sum().reset_index()

    # Plotar o gráfico de séries temporais
    st.subheader(f'Receita total por {title}')
    st.line_chart(revenue_by_period.set_index('periodo'))
def pre_process_model(df_model):

    def categorize_revenue(revenue):
        if revenue < 100:
            return 'Low'
        elif revenue < 1000:
            return 'Medium'
        else:
            return 'High'
    # Calcula a idade dos clientes com base na coluna 'birth_date'
    df_model['age'] = pd.Timestamp.now().year - df_model['birth_date'].dt.year

    # Calcula o tempo desde a última compra
    df_model['days_since_last_purchase'] = (pd.Timestamp.now() - df_model['last_date_purchase']).dt.days

    # Calcula o valor médio gasto por dia desde a última compra
    df_model['average_daily_expenditure'] = df_model['all_revenue'] / df_model['days_since_last_purchase']
    
    # Aplica a função à coluna 'all_revenue' para criar uma nova coluna 'revenue_category'
    df_model['revenue_category'] = df_model['all_revenue'].apply(categorize_revenue)

    # Tempo de assinatura: Diferença entre created_at e data atual
    df_model['subscription_duration'] = (pd.Timestamp.now() - df_model['created_at']).dt.days

    # Frequência de compra: all_orders / recency
    df_model['purchase_frequency'] = df_model['all_orders'] / df_model['recency']

    # Ticket médio por item: average_ticket / items_quantity
    df_model['average_ticket_per_item'] = df_model['average_ticket'] / df_model['items_quantity']

    # Média de receita por dia: all_revenue / recency
    df_model['average_daily_revenue'] = df_model['all_revenue'] / df_model['recency']

    # Indicador de churn: Flag para clientes que cancelaram a assinatura
    df_model['churn_indicator'] = df_model['status'].apply(lambda status: 1 if status == 'canceled' else 0)

    return df_model

# Função para verificar se o ID do cliente existe no DataFrame
def check_client_id(client_id, df):
    if client_id in df['id'].values:
        return True
    else:
        return False

with st.sidebar:
    selected = option_menu(
        "Menu",
        options=["Dashboard", "Predict Churn"],
        icons=["house", "list-task"],
    )

if selected == "Dashboard":


    df = load_data()
    # Adicionando uma opção extra para representar o valor nulo nos filtros
    states = [' '] + list(df['state'].unique())
    channels = [' '] + list(df['marketing_source'].unique())

    # Filtro de Estado
    selected_state = st.selectbox('Selecione um estado:', states)


    # KPIs
    st.header('KPIs')

    # Verifica se o usuário selecionou um estado ou canal de conversão antes de calcular os KPIs
    if selected_state == ' ':
        # Número total de clientes na base de dados
        total_subscription = df.shape[0]
        st.subheader('Número total de assinaturas:')

        # Número total de assinaturas por status
        total_active = df[df['status'] == 'active'].shape[0]
        total_paused = df[df['status'] == 'paused'].shape[0]
        total_canceled = df[df['status'] == 'canceled'].shape[0]

        # Criar as colunas para os KPIs
        col1, col2, col3, col4 = st.columns(4)

        # Exibir os KPIs
        col1.metric("Ativa", total_active)
        col2.metric("Pausada", total_paused)
        col3.metric("Cancelada", total_canceled)
        col4.metric("Total", total_subscription)

        # Calculo de churn
        negative = ((df.status == 'canceled') + (df.status == 'paused')).sum() # Somatória de assinaturas pausadas + canceladas
        positive = (df.status == 'active').sum() # Assinaturas ativas
        churn = round((negative / positive) * 100, 2) # Divisão dos clientes que cancelaram pelos clientes ativos

        # Receita total
        total_revenue = df['all_revenue'].sum()

        # Média de recência
        average_recency = df['recency'].mean()

        # Receita média por pedido
        average_revenue_per_order = df['average_ticket'].mean()

        # Número médio de itens por pedido
        average_items_per_order = df['items_quantity'].mean()

        # Taxa de conversão
        conversion_rate = df[df['all_orders'] > 0].shape[0] / total_active * 100

        # Exibir os KPIs em cada coluna
        col1.subheader('Taxa de churn')
        col1.write(f'{churn}%')

        col2.subheader('Receita total')
        col2.write(f'R${total_revenue:.2f}')

        col3.subheader('Média de recência')
        col3.write(f'{average_recency:.2f} dias')

        # Exibir os KPIs em cada coluna
        col1.subheader('Receita média por pedido:')
        col1.write(f'R${average_revenue_per_order:.2f}')

        col2.subheader('Número médio de itens por pedido:')
        col2.write(f'{average_items_per_order:.2f}')

        col3.subheader('Taxa de conversão:')
        col3.write(f'{conversion_rate:.2f}%')
        # Gráfico de pizza para percentual de canal de entrada
        st.header('Percentual de canal de entrada')
        marketing_source_count = df['marketing_source'].value_counts()
        fig = px.pie(names=marketing_source_count.index, values=marketing_source_count)
        st.plotly_chart(fig)
    else:
        df = df.query(f"state == '{selected_state}'")
        # Número total de clientes na base de dados
        total_subscription = df.shape[0]
        st.subheader('Número total de assinaturas:')
        # Número total de assinaturas por status
        total_active = df[df['status'] == 'active'].shape[0]
        total_paused = df[df['status'] == 'paused'].shape[0]
        total_canceled = df[df['status'] == 'canceled'].shape[0]

        # Criar as colunas para os KPIs
        col1, col2, col3, col4 = st.columns(4)
        # Exibir os KPIs
        col1.metric("Ativa", total_active)
        col2.metric("Pausada", total_paused)
        col3.metric("Cancelada", total_canceled)
        col4.metric("Total", total_subscription)
        # Calculo de churn
        negative = ((df.status == 'canceled') + (df.status == 'paused')).sum() # Somatória de assinaturas pausadas + canceladas
        positive = (df.status == 'active').sum() # Assinaturas ativas
        churn = round((negative / positive) * 100, 2) # Divisão dos clientes que cancelaram pelos clientes ativos
        # Receita total
        total_revenue = df['all_revenue'].sum()
        # Média de recência
        average_recency = df['recency'].mean()
        # Receita média por pedido
        average_revenue_per_order = df['average_ticket'].mean()
        # Número médio de itens por pedido
        average_items_per_order = df['items_quantity'].mean()
        # Taxa de conversão
        conversion_rate = df[df['all_orders'] > 0].shape[0] / total_active * 100
        # Exibir os KPIs em cada coluna
        col1.subheader('Taxa de churn')
        col1.write(f'{churn}%')
        col2.subheader('Receita total')
        col2.write(f'R${total_revenue:.2f}')
        col3.subheader('Média de recência')
        col3.write(f'{average_recency:.2f} dias')
        # Exibir os KPIs em cada coluna
        col1.subheader('Receita média por pedido:')
        col1.write(f'R${average_revenue_per_order:.2f}')
        col2.subheader('Número médio de itens por pedido:')
        col2.write(f'{average_items_per_order:.2f}')
        col3.subheader('Taxa de conversão:')
        col3.write(f'{conversion_rate:.2f}%')

        # Gráfico de pizza para percentual de canal de entrada
        st.header('Percentual de canal de entrada')
        marketing_source_count = df['marketing_source'].value_counts()
        fig = px.pie(names=marketing_source_count.index, values=marketing_source_count)
        st.plotly_chart(fig)

    # Plot dos gráficos temporais A para Anul e M para Mensal
    plot_revenue_by_period(df, 'M')
    plot_revenue_by_period(df, 'A')
    plot_cancelations_by_period(df, 'M')
    plot_cancelations_by_period(df, 'A')


    # Cidades mais lucrativas
    top_cities_revenue = df.groupby('city')['all_revenue'].sum().nlargest(5)
    st.subheader('Cidades mais lucrativas:')
    st.write(top_cities_revenue)

    # Estados com maior número de assinaturas
    subscriptions_by_state = pd.DataFrame(df.groupby('state').size().nlargest(5))

    # Renomear a coluna 0 para 'qtd_clientes_ativos'
    subscriptions_by_state = subscriptions_by_state.rename(columns={0: 'qtd_clientes_ativos'})
    st.subheader('Estados com maior número de assinaturas:')
    st.write(subscriptions_by_state)

    # Fontes de marketing mais eficazes
    top_marketing_sources = pd.DataFrame(df.groupby('marketing_source').size().nlargest(5))
    top_marketing_sources = top_marketing_sources.rename(columns={0: 'qtd_clientes_ativos'})
    st.subheader('Fontes de marketing mais eficazes:')
    st.write(top_marketing_sources)

    # Distribuição de recência
    st.header('Distribuição de recência dos usuários:')
    recency_distribution = df['recency'].dropna().value_counts().sort_index()
    st.line_chart(recency_distribution)

    # Filtrar os dados para os três tipos de status
    group1_data = df[df['status'] == 'active']['average_ticket']
    group2_data = df[df['status'] == 'paused']['average_ticket']
    group3_data = df[df['status'] == 'canceled']['average_ticket']

    # Agrupar os dados para criar o gráfico de distribuição
    hist_data = [group1_data, group2_data, group3_data]
    group_labels = ['Active', 'Paused', 'Canceled']

    # Criar o gráfico de distribuição com o Plotly
    fig = ff.create_distplot(hist_data, group_labels, show_hist=False, show_rug=True)

    # Adicionar título ao gráfico
    fig.update_layout(
        title_text="Distribuição do Ticket Médio por Status",
        xaxis_title="Average Ticket",
        yaxis_title="Density"
    )

    # Plotar o gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)

elif selected == "Predict Churn":
    columns = [
                'average_ticket'    
                ,'items_quantity'    
                ,'all_revenue'       
                ,'all_orders'        
                ,'recency'
                ,'age' 
                ,'days_since_last_purchase' 
                ,'average_daily_expenditure'         
                ,'subscription_duration'    
                ,'purchase_frequency'       
                ,'average_ticket_per_item'  
                ,'average_daily_revenue'    
                ,'marketing_source'
                ,'purchase_frequency'
                ,'revenue_category'
                ]

    df = load_data()

    # Criando interface do usuário
    with st.form("dados_cliente"):
        st.title("Caixa de entrada para ID do cliente")

        # Caixa de entrada de texto para o ID do cliente
        client_id = st.text_input("Insira o ID do cliente:")

        submitted = st.form_submit_button("Enviar")
        # Verificar se o ID do cliente está presente no DataFrame
        if submitted:
            if check_client_id(client_id, df):
                df_filtered = df.query(f'id == "{client_id}"')
                df_filtered = pre_process_model(df_filtered)

                df_filtered = df_filtered[columns]

                probabilidade_churn = model.predict_proba(df_filtered)
                probabilidade_churn = probabilidade_churn[0][1] * 100
                probabilidade_churn = str(round(probabilidade_churn, 2))
                probabilidade_churn = probabilidade_churn.rstrip('0').rstrip('.')


                st.success(f"Probabilidade de Churn: {probabilidade_churn}%")


            else:
                st.error("Dados incorretos. Por favor, digite novamente.")

