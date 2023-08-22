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
    
def maior_idd (df):
    maior_idade = df.loc[:, "Delivery_person_Age"].max()
    col1.metric('Maior idade é:', maior_idade)
def menor_idd(df):
    menor_idade = df.loc[:, "Delivery_person_Age"].min()
    col2.metric('Menor idade é:', menor_idade)
def mhr_cond_vei (df):
    maior_avl = df.loc[:, "Vehicle_condition"].max()
    col3.metric('Melhor condicao é:', maior_avl)
def pior_cond_vei (df):
    menor_avl = df.loc[:, "Vehicle_condition"].min()
    col4.metric('Pior condicao é:', menor_avl)
def mean_entr (df):
    rnk_avl=(round(df.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']].groupby( 'Delivery_person_ID' ).mean().reset_index(), 1))
    st.dataframe(rnk_avl, use_container_width=True, height=530)
def mean_trans(df):
    df_mean_std = df.loc[:, ['Road_traffic_density', 'Delivery_person_Ratings']].groupby( 'Road_traffic_density'   ).agg({'Delivery_person_Ratings':['mean','std']})
    df_mean_std.columns=['delivery_mean', 'delivery_std']
    df_mean_std = df_mean_std.reset_index()
    rnk_trns=round(df_mean_std,2)
    st.dataframe(rnk_trns, use_container_width=True)
def mean_avl(df):
    df_mean_std_cond = df.loc[:, ['Weatherconditions', 'Delivery_person_Ratings']].groupby( 'Weatherconditions' ).agg({'Delivery_person_Ratings':['mean','std']})
    df_mean_std_cond.columns=['delivery_mean', 'delivery_std']
    df_mean_std_cond = df_mean_std_cond.reset_index()
    rnk_cond=round(df_mean_std_cond,2)
    st.dataframe(rnk_cond, use_container_width=True)
def fast_ent(df):
    dfspeed = df.loc[:, ['Delivery_person_ID', 'Time_taken(min)', 'City']].groupby(['City', 'Delivery_person_ID'] ).min().sort_values(['City', 'Time_taken(min)'], ascending=True).reset_index()
    dfm = dfspeed.loc[dfspeed['City']=='Metropolitian',:].head(5)
    dfu = dfspeed.loc[dfspeed['City']=='Urban',:].head(5)
    dfsu = dfspeed.loc[dfspeed['City']=='Semi-Urban',:].head(5)
    dfspymin = pd.concat([dfm, dfu, dfsu]).reset_index(drop=True)
    top_min=(dfspymin)
    st.dataframe(top_min,use_container_width=True)
def slow_ent(df):
    dfspeedm = df.loc[:, ['Delivery_person_ID', 'Time_taken(min)', 'City']].groupby(['City', 'Delivery_person_ID'] ).max().sort_values(['City', 'Time_taken(min)'], ascending=False).reset_index()
    dfmm = dfspeedm.loc[dfspeedm['City']=='Metropolitian',:].head(10)
    dfum = dfspeedm.loc[dfspeedm['City']=='Urban',:].head(10)
    dfsum = dfspeedm.loc[dfspeedm['City']=='Semi-Urban',:].head(10)
    dfspymax = pd.concat([dfmm, dfum, dfsum]).reset_index(drop=True)
    top_max=dfspymax
    st.dataframe(top_max, use_container_width=True)
##-------------------------------------------------------------------------------------------------------------

df = clean_code(df)
st.set_page_config(layout="wide")

# =================================================================================
#
# Sidebar
#
# =================================================================================

st.header('Marketplace - Visão Entregadores')

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','',''])
with tab1:
## Medições container superior ------------------------------------------------------------------------------------------------------------------------------------    
    with st.container():
        
        col1, col2, col3, col4 = st.columns (4, gap='Large')
        with col1:
            maior_idd(df)
        with col2:
            menor_idd(df)
        with col3:
            mhr_cond_vei (df)
        with col4:
            pior_cond_vei (df)
# =================================================================================
# =================================================================================         
    with st.container():
        st.title('Avaliacoes')
        col1, col2 = st.columns (2)
        with col1:
            st.subheader('Avaliação média por entregador')
            mean_entr(df)
        with col2:
            st.subheader('Avaliação média por transito')
            mean_trans(df)
            st.subheader('Avaliação média por clima')
            mean_avl(df)       
# =================================================================================
# Parte Inferior Dashboard
# =================================================================================
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de entrega')
        col1, col2 = st.columns (2)
        with col1:
            st.subheader('Top entregadores mais rapidos')
            fast_ent(df)
        with col2:
            st.subheader('Top entregadores mais lentos')
            slow_ent(df)
            




























































