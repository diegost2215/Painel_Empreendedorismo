import pandas as pd
import streamlit as st
from copy import deepcopy
import requests
import plotly.express as px
import geopandas as gpd


#Em desenvolvimento
mypallete = list(px.colors.qualitative.Antique) + list(px.colors.qualitative.T10)
st.set_page_config(layout ="wide", initial_sidebar_state="auto")

data_atualizacao = 'outubro-2025'

populacoes_censo = {'Itajaí':264054, 'Balneário Camboriu':139155,'Blumenau':385558, 'Brusque':141385, 'Navegantes':86401, 'Joinville':616317,
                    'Florianópolis':537211, 'São José':270299, 'Chapecó':254785, 'Palhoça':222598, 'Criciúma':214493, 'Jaraguá do Sul':182660,
                    'Lages':164981}
@st.cache_data
def load_data():
  data = pd.read_parquet('Arquivos/data_cr.parquet')
  municipios_de_interesse = {'8161':'Itajaí', '8039':'Balneário Camboriu','8047':'Blumenau', '8055':'Brusque', '8221':'Navegantes', '8179':'Joinville',
                           '8105':'Florianópolis', '8327':'São José', '8081':'Chapecó', '8233':'Palhoça', '8089':'Criciúma', '8175':'Jaraguá do Sul',
                           '8183':'Lages'  }
  data['Município_nome'] = data['Município'].map(municipios_de_interesse)
  data_tree_map = deepcopy(data[(data['Município_nome']=='Itajaí') & (data['Situação_Cadastral']=='02') & (data['CNAE_principal']!='8888888')])
  geodata = gpd.read_parquet('Arquivos/data_Itajai_ativas_georef.parquet')
  
  Cnae_pai = pd.read_csv('Arquivos/CNAE_grupo.txt', dtype = str, sep = ':', )
  Cnae_pai.set_index('Cnae', inplace=True)
  Cnae_pai_dict = Cnae_pai['Grupo'].to_dict()

  Cnae_divisao = pd.read_csv('Arquivos/Cnae_divisao.txt', dtype = str, sep = ':', )
  Cnae_divisao.set_index('CNAE', inplace=True)
  Cnae_divisao_dict = Cnae_divisao['Divisão'].to_dict()

  Cnae_subdivisao = pd.read_csv('Arquivos/Cnae_subdivisao.txt', dtype = str, sep = '|', )
  Cnae_subdivisao.set_index('CNAE', inplace=True)
  Cnae_subdivisao_dict = Cnae_subdivisao['Subdivisao'].to_dict()
  
  return data, geodata, data_tree_map, Cnae_pai_dict, Cnae_divisao_dict, Cnae_subdivisao_dict


data, geodata, data_tree_map, Cnae_pai_dict, Cnae_divisao_dict, Cnae_subdivisao_dict = load_data()

col0A,  col0B = st.columns([0.85,0.15])
with col0A:
   st.header('Painel do Empreendedorismo - Itajaí - Em Desenvolvimento-Revisar')
   #st.image(image='banner3 - Copia.png')
with col0B:
  st.caption('')
  st.caption('')
  st.caption(f'Última Atualização em {data_atualizacao}')


##########################################################transformar ano em variável....
with st.container(border=True):
  col1A,col1B, col1C, col1D = st.columns([0.25,0.25, 0.25, 0.25])
  with col1A:
      empresas_ativas_contagem = len((data[(data['Situação_Cadastral']=='02') & (data['Município_nome']=='Itajaí')]))
      st.metric(label = f"Empresas-2025", value = f"{empresas_ativas_contagem:.0f} CNPJs Ativos", )

  with col1B:
      CNPJs_abertos_contagem = len(data[(data['Ano_início']==2025) & (data['Município_nome']=='Itajaí')])
      CNPJs_abertos_contagem_anoanterior = len(data[(data['Ano_início']==2024) & (data['Município_nome']=='Itajaí')])
      delta_aberturas = (CNPJs_abertos_contagem-CNPJs_abertos_contagem_anoanterior)/CNPJs_abertos_contagem_anoanterior
      st.metric(label = f"Novas Empresas-2025", value = f"{CNPJs_abertos_contagem:.0f} CNPJs", 
      delta = f'{delta_aberturas:.2%} em relação à {2024}')
    
  with col1C:
      CNPJs_baixados_contagem = len(data[(data['Ano_situação_cadastral']==2025) & (data['Município_nome']=='Itajaí') & (data['Situação_Cadastral']!='02')])
      CNPJs_baixados_contagem_anoanterior = len(data[(data['Ano_situação_cadastral']==2024) & (data['Município_nome']=='Itajaí') & (data['Situação_Cadastral']!='02')])
      delta_baixa = (CNPJs_baixados_contagem-CNPJs_baixados_contagem_anoanterior)/CNPJs_baixados_contagem_anoanterior
      st.metric(label = f"Desativações Empresas-2025", value = f"{CNPJs_baixados_contagem:.0f} CNPJs", 
      delta = f'{delta_baixa:.2%} em relação à {2024}')
    


    #####################################
with st.container(border=True):
  col2A, col2B =  st.columns([0.3,0.7])
  with col2A:
    percapita = {'per 1000 hab':'por_1000_hab','total':'CNPJ' }
    percapita_escolha = st.pills(label = '', options = ['per 1000 hab', 'total'], selection_mode = 'single', default = ['per 1000 hab'])
  with col2B:
    data['Cnae_pai'] = data['CNAE_principal'].str[:2]
    options_cnaes = data['Cnae_pai'].unique()
    Cnaes_selecionados = st.multiselect('Selecione o(s) Cnae(s)', options = options_cnaes ,  default = ['46', '49','50','51','52','53'],                                    
                                      width="stretch")
 
  
  data_f_CNAE = deepcopy(data[(data['Cnae_pai'].isin(Cnaes_selecionados))].reset_index())


  CNPJ_ativos = pd.pivot_table(data =data_f_CNAE[data_f_CNAE['Situação_Cadastral']=='02'], index = ['Município_nome', 'Tipo'],
                            values='CNPJ', aggfunc='count', fill_value=0)

  CNPJ_ativos.reset_index(inplace=True)
  CNPJ_ativos['População_Censo_2022'] = CNPJ_ativos['Município_nome'].map(populacoes_censo)
  CNPJ_ativos['por_1000_hab'] = CNPJ_ativos['CNPJ']/CNPJ_ativos['População_Censo_2022']*1000
  fig2A = px.bar(CNPJ_ativos, y=percapita[percapita_escolha],
                 x='Município_nome',
                 title = f'Empresas Ativas - Cnaes Selecionados' ,
                 template = 'plotly_white', color = 'Tipo',color_discrete_sequence=mypallete,  text_auto='.2s')
  #fig2A.update_traces(width=1, texttemplate='R$ %{x:.3s}')
  fig2A.update_layout(xaxis_title=None, yaxis_title=None, title={'x': 0.5,'xanchor': 'center'} )
  st.plotly_chart(fig2A,use_container_width=True,)

  
  CNPJ_abertos = pd.pivot_table(data =data_f_CNAE[data_f_CNAE['Ano_início']>2018], index = ['Município_nome', 'Ano_início'],
                            values='CNPJ', aggfunc='count', fill_value=0)
  CNPJ_abertos.reset_index(inplace=True)
  #CNPJ_abertos['Ano_início'] =   CNPJ_abertos['Ano_início'].astype(str)
  CNPJ_abertos['População_Censo_2022'] = CNPJ_abertos['Município_nome'].map(populacoes_censo)
  CNPJ_abertos['por_1000_hab'] = CNPJ_abertos['CNPJ']/CNPJ_abertos['População_Censo_2022']*1000

  fig2B = px.bar(CNPJ_abertos,  x='Ano_início',y=percapita[percapita_escolha],template = 'plotly_white', color_discrete_sequence=mypallete,   text_auto='.2s',color = 'Município_nome',
                barmode='group', title = f'Novos CNPJs 2025 - Cnaes Selecionados', ) 
                 
  fig2B.update_layout(xaxis_title=None, yaxis_title=None, title={'x': 0.5,'xanchor': 'center'} )
  st.plotly_chart(fig2B,use_container_width=True, )

  geodata['Cnae_pai'] = geodata['CNAE_principal'].str[:2]
  geodata_f_cnae = deepcopy(geodata[(geodata['Cnae_pai'].isin(Cnaes_selecionados))].reset_index())
  
  geodata_f_cnae.insert(0,column='Longitude', value= geodata_f_cnae.get_coordinates()['x'])
  geodata_f_cnae.insert(0,column='Latitude', value= geodata_f_cnae.get_coordinates()['y'])
  geodata_f_cnae['dummy_size'] = 3


  fig2C = px.scatter_map(geodata_f_cnae, lat="Latitude", lon="Longitude", zoom=13, center= {'lat':-26.91, 'lon':-48.67},
                     map_style ='streets', color = 'Cnae_pai', height = 800, hover_data  = 'CNPJ', size = 'dummy_size')
  fig2C.update_traces(cluster=dict(enabled=True))
  st.plotly_chart(fig2C,use_container_width=True, )


with st.container(border=True):  
  data_tree_map['Cnae_pai'] = data_tree_map['CNAE_principal'].str[:2].map(Cnae_pai_dict)
  data_tree_map['Cnae_divisao'] = data_tree_map['CNAE_principal'].str[:2].map(Cnae_divisao_dict)
  data_tree_map['Cnae_subdivisao'] = data_tree_map['CNAE_principal'].str[:2] + '.' + data_tree_map['CNAE_principal'].str[2:3]
  data_tree_map['Cnae_subdivisao'] = data_tree_map['Cnae_subdivisao'].map(Cnae_subdivisao_dict)
  #data_tree_map['Cnae_pai'] = data_tree_map['Cnae_pai']
  
  fig3 = px.treemap(data_tree_map, path=[px.Constant("CNAE"),'Cnae_pai', 'Cnae_divisao', 'Cnae_subdivisao', 'CNAE_principal'], maxdepth=2, color_discrete_map={'(?)':'white'},
                    color_discrete_sequence=mypallete)
  
  fig3.update_traces(textinfo='label+percent root')
  fig3.update_traces(hovertemplate='%{label}<br>',textfont=dict(size=20), marker=dict(cornerradius=8), marker_line_color="black")
  fig3.update_layout(margin=dict(t=0, b=0))
  st.plotly_chart(fig3, use_container_width=True)



  #data_tree_map['CNAE_divisao'] = data_tree_map['CNAE_principal'].str[:2]
  #data_tree_map['Cnae_detalhado'] = data_tree_map['CNAE_principal'].str[:2]
  #Cnae_pai


