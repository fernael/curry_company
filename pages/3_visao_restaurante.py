import pandas as pd
import re
import plotly.express as px
import folium as fl
from haversine import haversine
import streamlit as st
from datetime import datetime as dt
from PIL import Image
from streamlit_folium import folium_static
import plotly.graph_objects as go
import numpy  as np


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
    
def unic_emtr(df):
    delivery = len ( df.loc[:,"Delivery_person_ID"].unique())
    col1.metric('Entregadores únicos', delivery )
    
def dist_mean(df):
    cols = ['Restaurant_latitude','Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df["Distancias"]=df.loc[:, cols].apply(lambda x: haversine((x["Restaurant_latitude"],x["Restaurant_longitude"]),(x["Delivery_location_latitude"],x["Delivery_location_longitude"])), axis=1)
    avg_dist=round(df["Distancias"].mean(),2)
    col2.metric('Distância média', avg_dist )
    
def fest_time(df):
    cols = ['Time_taken(min)', 'Festival']
    df_fest_std_mean = round(df.loc[:, cols].groupby(['Festival']).agg({'Time_taken(min)': ['mean', 'std']}),2)
    df_fest_std_mean.columns = ['mean_time', 'std_time']
    dff_mean_std = pd.DataFrame(df_fest_std_mean.reset_index())
    mean_yes = dff_mean_std.iloc[1,1]
    col3.metric('Tempo médio Fest', mean_yes )
    
def desv_fest_time (df):
    cols = ['Time_taken(min)', 'Festival']
    df_fest_std_mean = round(df.loc[:, cols].groupby(['Festival']).agg({'Time_taken(min)': ['mean', 'std']}),2)
    df_fest_std_mean.columns = ['mean_time', 'std_time']
    dff_mean_std = pd.DataFrame(df_fest_std_mean.reset_index())
    std_yes = dff_mean_std.iloc[1,2]
    col4.metric('Desvio padão Fest', std_yes )
    
def dia_comum(df):
    cols = ['Time_taken(min)', 'Festival']
    df_fest_std_mean = round(df.loc[:, cols].groupby(['Festival']).agg({'Time_taken(min)': ['mean', 'std']}),2)
    df_fest_std_mean.columns = ['mean_time', 'std_time']
    dff_mean_std = pd.DataFrame(df_fest_std_mean.reset_index())
    mean_no = dff_mean_std.iloc[0,1]
    col5.metric('Dia comum médio', mean_no )
    
def dia_comum_desv(df):
    cols = ['Time_taken(min)', 'Festival']
    df_fest_std_mean = round(df.loc[:, cols].groupby(['Festival']).agg({'Time_taken(min)': ['mean', 'std']}),2)
    df_fest_std_mean.columns = ['mean_time', 'std_time']
    dff_mean_std = pd.DataFrame(df_fest_std_mean.reset_index())
    std_no = dff_mean_std.iloc[0,2]
    col6.metric('Dia comum desv pad', std_no )
    
def temp_med_ent_cd(df):
    df_aux = df.loc[:, ['City', 'Time_taken(min)']].groupby( 'City' ).agg( {'Time_taken(min)': ['mean', 'std']} )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure() 
    fig.add_trace( go.Bar( name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time']))) 
    fig.update_layout(barmode='group') 
    st.plotly_chart( fig, use_container_width=True )
    
def temp_med_ent_ped(df):
    df_aux = ( df.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']]
                  .groupby( ['City', 'Type_of_order'] )
                  .agg( {'Time_taken(min)': ['mean', 'std']} ) )

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    st.dataframe( df_aux, use_container_width=True )
    
def dist_mean_porc(df):
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    df['distance'] = df.loc[:, cols].apply( lambda x: 
                                haversine(  (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                            (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )
    avg_distance = df.loc[:, ['City', 'distance']].groupby( 'City' ).mean().reset_index()
    fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
    fig = fig.update_layout(width=900,height=900)
    st.plotly_chart( fig, use_container_width=True)

def tp_urb_dens(df):
    df_aux = ( df.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
                  .groupby( ['City', 'Road_traffic_density'] )
                  .agg( {'Time_taken(min)': ['mean', 'std']} ) )

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                      color='std_time', color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(df_aux['std_time'] ) )
    fig = fig.update_layout(width=800,height=800)
    st.plotly_chart( fig, use_container_width=True)
##-------------------------------------------------------------------------------------------------------------

df = clean_code(df)
st.set_page_config(layout="wide")

# =================================================================================
# Sidebar
# =================================================================================

st.header('Marketplace - Visão Restaurantes')

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
# Layout 
# =================================================================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial','',''])
with tab1:
    with st.container():
        st.title('Metricas')
        col1, col2, col3, col4, col5, col6 = st.columns(6, gap='large')
        with col1:
            unic_emtr(df)
        with col2:
            dist_mean(df)
        with col3:
            fest_time(df)
        with col4:
            desv_fest_time (df)
        with col5:
            dia_comum(df)
        with col6:
            dia_comum_desv(df)
# =================================================================================
# Colunas graficos
# =================================================================================
    with st.container():
        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown("#### Distância média em %")
            dist_mean_porc(df)
        with col2:
            st.markdown("#### Distribuição Tipo urbano/densidade")
            st.markdown("#### ")
            st.markdown("#### ")
            tp_urb_dens(df)       
# =================================================================================
# Colunas graficos/tabela
# =================================================================================        
    with st.container():
        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown("#### Tempo médio e desvio padrão de entrega por cidade")
            temp_med_ent_cd(df)
        with col2:
            st.markdown("#### Tempo médio e desvio padrão por tipo de pedido")
            temp_med_ent_ped(df)
            
