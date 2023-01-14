#!/usr/bin/env python
# coding: utf-8

# In[10]:


import streamlit as st  # pip install streamlit
import pandas as pd  # pip install pandas
# import plotly.express as px  # pip install plotly-express
import base64  # Standard Python Module
from io import StringIO, BytesIO  # Standard Python Module

import folium
from folium import plugins
from streamlit_folium import st_folium



# import matplotlib as mpl
# import matplotlib.pyplot as plt
# import matplotlib.font_manager as fm










def generate_excel_download_link(df):
    # Credit Excel: https://discuss.streamlit.io/t/how-to-add-a-download-excel-csv-function-to-a-button/4474/5
    towrite = BytesIO()
    df.to_excel(towrite, encoding="utf-8", index=False, header=True)  # write to BytesIO buffer
    towrite.seek(0)  # reset pointer
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="data_download.xlsx">Download Excel File</a>'
    return st.markdown(href, unsafe_allow_html=True)

def generate_html_download_link(ddf):
    # Credit Plotly: https://discuss.streamlit.io/t/download-plotly-plot-as-html/4426/2
    # towrite = StringIO()
    towrite = BytesIO(towrite.getvalue().encode())    
    # ddf.write_html(towrite, include_plotlyjs="cdn")
    
    ddf.save(towrite, close_file=True)

    b64 = base64.b64encode(towrite.read()).decode()
        
    href = f'<a href="data:text/html;charset=utf-8;base64, {b64}" download="듀얼맵.html">Download 듀얼맵</a>'
    return st.markdown(href, unsafe_allow_html=True)


st.set_page_config(layout="wide")
st.title('맵만들기..? 📈')
st.subheader('엑셀파일을 아래에.... 올리면?')

uploaded_file = st.file_uploader('Choose a XLSX file', type='xlsx')
if uploaded_file:
    st.markdown('---')
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    st.dataframe(df)
    
    
    df1 = pd.read_excel('data/location.xlsx')
    dfa = pd.merge(df,df1, left_on='고교코드',right_on='NEIS_CODE', how='left')
    
    
    
    choice = ['종합','교과']
    choice_selected = st.selectbox("선택해주세요", choice)
    
    
    df종합 = dfa[dfa['전형유형']=='학생부종합']
    df교과 = dfa[dfa['전형유형']=='학생부교과']
    
    df종합1 = df종합[df종합['지원자']>=5]
    df교과1 = df교과[df교과['지원자']>=5]
    
    
    import json
    
    state_geo = 'data/SIG.geojson'
    state_geo1 = json.load(open(state_geo, encoding ='utf-8'))
    
    
    regional_count종합1=df종합1[['위도','경도']]
    regional_count종합=df종합[['위도','경도']]

    regional_count교과1=df교과1[['위도','경도']]
    regional_count교과=df교과[['위도','경도']]
    
    df종합11 = pd.DataFrame(df종합1.groupby(['SIG_CD','고교지역','고교세부지역'])['지원자'].sum()).reset_index()
    df종합11['SIG_CD'] = df종합11['SIG_CD'].astype(str)
    df종합00 = pd.DataFrame(df종합.groupby(['SIG_CD','고교지역','고교세부지역'])['지원자'].sum()).reset_index()
    df종합00['SIG_CD'] = df종합00['SIG_CD'].astype(str)
    
    
    
    df교과11 = pd.DataFrame(df교과1.groupby(['SIG_CD','고교지역','고교세부지역'])['지원자'].sum()).reset_index()
    df교과11['SIG_CD'] = df교과11['SIG_CD'].astype(str)
    df교과11['지원자'] = df교과11['지원자'].astype(int)
    df교과00 = pd.DataFrame(df교과.groupby(['SIG_CD','고교지역','고교세부지역'])['지원자'].sum()).reset_index()
    df교과00['SIG_CD'] = df교과00['SIG_CD'].astype(str)
    df교과00['지원자'] = df교과00['지원자'].astype(int)
    
    

    
    
    from folium.features import DivIcon
    m = folium.plugins.DualMap(location = [35.8,127.7], tiles = 'OpenStreetMap', zoom_start=7)


    choropleth = folium.Choropleth(
        geo_data=state_geo1,
        name='sigun_people',
        data=eval('df'+choice_selected+'00'),
        columns = ['SIG_CD','지원자'],
        key_on = 'feature.properties.SIG_CD',
        nan_fill_color='black',
        fill_color='BuPu',
        fill_opactiy=0.7,
        line_opacity=0.5,
        legend_name='jonghab_all'
    ).add_to(m.m1) 


    plugins.Fullscreen(position='topright',
                       title='Click to Expand',
                       title_cancel='Click to Exit',
                       force_separate_button=True).add_to(m.m1)
    plugins.MousePosition().add_to(m.m1)
    plugins.MarkerCluster(eval('regional_count'+choice_selected)).add_to(m.m1)


    choropleth = folium.Choropleth(
        geo_data=state_geo1,
        name='sigun_people',
        data=eval('df'+choice_selected+'11'),
        columns = ['SIG_CD','지원자'],
        key_on = 'feature.properties.SIG_CD',
        nan_fill_color='black',
        fill_color='RdPu',
        fill_opactiy=0.7,
        line_opacity=0.5,
        legend_name='jonghab_over5'
    ).add_to(m.m2)

    plugins.Fullscreen(position='topright',
                     title='Click to Expand',
                     title_cancel='Click to Exit',
                     force_separate_button=True).add_to(m.m2)
    plugins.MousePosition().add_to(m.m2)
    plugins.MarkerCluster(eval('regional_count'+choice_selected+'1')).add_to(m.m2)
    
    m.save("듀얼맵.html", close_file=True)
    
    st_folium(m)
    
    
    
    
#     groupby_column = st.selectbox(
#         'What would you like to analyse?',
#         ('Ship Mode', 'Segment', 'Category', 'Sub-Category'),
#     )

    # -- GROUP DATAFRAME
#     output_columns = ['Sales', 'Profit']
#     df_grouped = df.groupby(by=[groupby_column], as_index=False)[output_columns].sum()

    # -- PLOT DATAFRAME
#     fig = px.bar(
#         df_grouped,
#         x=groupby_column,
#         y='Sales',
#         color='Profit',
#         color_continuous_scale=['red', 'yellow', 'green'],
#         template='plotly_white',
#         title=f'<b>Sales & Profit by {groupby_column}</b>'
#     )
#     st.plotly_chart(fig)

    # -- DOWNLOAD SECTION
    st.subheader('Downloads:')
    generate_excel_download_link(dfa)
    generate_html_download_link(m)






