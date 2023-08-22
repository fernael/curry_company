import streamlit as st
from PIL import Image

st.set_page_config(
        page_title="Home"    
)
image_path='Cuty Company Logo - Black with White Background - 5000x5000.png'
image=Image.open(image_path)
st.sidebar.image(image, width=300)

st.sidebar.markdown("# Cury Company")
st.sidebar.markdown("## Fastest Delivery in Town")

st.write("# Cury Company Growth Dashboard")

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Dashboard?
    - Visão Empresa:
        - Visão gerencial: Métricas gerais de comportamento.
        - Visão Tática: INdicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crecimento.
    - Visão Restaurante:
        - Semanais de crescimento dos restaurantes
    """)