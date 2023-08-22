import pandas as pd
import re
import plotly.express as px
import folium as fl
from haversine import haversine
import streamlit as st
from datetime import datetime as dt
from PIL import Image
from streamlit_folium import folium_static


df_raw = pd.read_csv('train.csv')

df_raw.head()

# Fazendo uma cópia do DataFrame Lido
df = df_raw.copy()


## Funções ------------------------------------------------------------------------------------------------------------------------------------
def clean_code(df):
    '''
    Está função tem a responsabilidade de limpar o dataframe
    Tipos de limpeza:
    1 Remoção dos dados NaN
    2 Mudança do tipo de dado da coluna
    3 Remoção dos espaços das variáveis
    4 Formatação da coluna das datas
    5 Limpeza da coluna tempo
    '''
    # Remover spaco da string
    df['ID'] = df['ID'].str.strip()
    df['Delivery_person_ID'] = df['Delivery_person_ID'].str.strip()
    df['Festival'] = df['Festival'].str.strip()
    df['City'] = df['City'].str.strip()
    df['Road_traffic_density'] = df['Road_traffic_density'].str.strip()
    
    # Excluir as linhas com a idade dos entregadores vazia
    # ( Conceitos de seleção condicional )
    linhas_vazias = df['Delivery_person_Age'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = df['City'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = df['City'] != 'NaN'
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = df['Road_traffic_density'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = df['Festival'] != 'NaN'
    df = df.loc[linhas_vazias, :]
    
    # Conversao de texto/categoria/string para numeros inteiros
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int )
    
    # Conversao de texto/categoria/strings para numeros decimais
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float ).copy()
    
    # Conversao de texto para data
    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )
    
    # Remove as linhas da culuna multiple_deliveries que tenham o
    # conteudo igual a 'NaN '
    linhas_vazias = df['multiple_deliveries'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    df['multiple_deliveries'] = df['multiple_deliveries'].astype( int ).copy()
    
    # Comando para remover o texto de números
    df = df.reset_index( drop=True )
    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split('(min)')[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

    return df

def quant_ped (df):
    df_aux = df.loc[:, ['ID', 'Order_Date']].groupby( 'Order_Date' ).count().reset_index()
    df_aux.columns = ['Periodos_Entregas', 'Volumetria']
    fig = px.bar( df_aux, x='Periodos_Entregas', y='Volumetria' )
    return fig
    
def dist_ped_traf(df):
    columns = ['ID', 'Road_traffic_density']
    df_aux = df.loc[:, columns].groupby( 'Road_traffic_density' ).count().reset_index()
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
    figpz =px.pie( df_aux, values='perc_ID', names='Road_traffic_density' )
    return figpz
    
def camp_vol_traf(df):
    columns = ['ID', 'City', 'Road_traffic_density']
    df_aux = df.loc[:, columns].groupby( ['City', 'Road_traffic_density'] ).count().reset_index()
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
    figbar =px.bar( df_aux, x='City', y='ID', color='Road_traffic_density', barmode='group')
    return figbar
    
def quant_ped_sm(df):
    df['week_of_year'] = df['Order_Date'].dt.strftime( "%U" )
    df_aux = df.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    df_aux.columns = ['Semana_Ano', 'Volumetria']
    figsm = px.line( df_aux, x='Semana_Ano', y='Volumetria' )
    return figsm

def quant_ped_ent(df):
    df_aux1 = df.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    df_aux2 = df.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year').nunique().reset_index()
    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    figsm = px.line( df_aux, x='week_of_year', y='order_by_delivery' )
    return figsm
    
def map_dlv(df):
        columns = ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']
        columns_groupby = ['City', 'Road_traffic_density']
        data_plot = df.loc[:, columns].groupby( columns_groupby ).median().reset_index()
        map = fl.Map( zoom_start=11 )
        for index, location_info in data_plot.iterrows():
            fl.Marker( [location_info['Delivery_location_latitude'],
            location_info['Delivery_location_longitude']],
            popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )
        folium_static(map, width=1024, height=800)
##-------------------------------------------------------------------------------------------------------------




df = clean_code(df)

st.set_page_config(layout="wide")

# =================================================================================
#
# Sidebar
#
# =================================================================================
st.header('Marketplace - Visão Clientes')

image_path='Cuty Company Logo - Black with White Background - 5000x5000.png'
image=Image.open(image_path)
st.sidebar.image(image, width=300)
st.sidebar.markdown("""---""")

date_slider = st.sidebar.slider('Selecione o intervalo',
                                value = dt(2022,4,13), 
                                min_value= dt(2022,2,11), 
                                max_value= dt(2022,4,6),
                                format='DD-MM-YYYY')
st.sidebar.markdown("""---""")

traffic_options=st.sidebar.multiselect('Quais as condições do trânsito?',
                      ['Low','Medium','High','Jam'],
                      default=['Low','Medium','High','Jam'])

st.sidebar.markdown("""---""")

line_od = df['Order_Date']< date_slider
df=df.loc[line_od, :]

line_td = df['Road_traffic_density'].isin(traffic_options)
df=df.loc[line_td,:]

# =================================================================================
#
# Layout 
#
# =================================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:

# =================================================================================
# Quantidade de pedidos por dia
# =================================================================================
    with st.container():
        st.header('Quantidade de pedidos por dia')
        fig = quant_ped (df)
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container():
# =================================================================================
# Quantidade de pedidos por dia
# =================================================================================
        col1, col2 = st.columns(2)
        
        with col1:
            st.header('Distribuição dos pedidos por tipo de tráfego')
            figpz = dist_ped_traf(df)
            st.plotly_chart(figpz, use_container_width=True)
            
        with col2:
            st.header('Comparação do volume de pedidos por cidade e tipo de tráfego')
            figbar = camp_vol_traf(df)
            st.plotly_chart(figbar, use_container_width=True)

with tab2:

# =================================================================================
# Quantidade de pedidos por semana/A quantidade de pedidos por entregador por semana
# =================================================================================
    
    with st.container():
        st.header('Quantidade de pedidos por semana')
        figsm = quant_ped_sm(df)
        st.plotly_chart(figsm, use_container_width=True)
        
    with st.container():
        
        st.header('A quantidade de pedidos por entregador por semana')
        figsm = quant_ped_ent(df)

        st.plotly_chart(figsm, use_container_width=True)

with tab3:

# =================================================================================
# A localização central de cada cidade por tipo de tráfego
# =================================================================================

    st.header('A localização central de cada cidade por tipo de tráfego')
    map_dlv(df)
    
    


































































































