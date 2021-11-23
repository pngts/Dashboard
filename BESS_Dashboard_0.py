# -*- coding: utf-8 -*-
"""
Created on Fri Nov 19 13:19:41 2021

@author: PanagiotisErodotou
"""
#streamlit run BESS_Dashboard_0.py
###### Create Dashboard  for Bess #####
import psycopg2
import pandas as pd
import numpy as np

import  streamlit as st
import plotly.express as px


    # In[ ]: START
def load_Data_from_sql(battery_pack_id):
    
# some options to make dataframes display better on screen:
    pd.set_option('display.max_columns', None)
    pd.set_option('expand_frame_repr', False)   
    #print('Getting data from server for battery: ',str(battery_id) )
    # set up input data connection:
    conn_details = ['postgres', 'energylancaster',
                    'database-dapp-prod-01.ciw65t1507ge.eu-west-2.rds.amazonaws.com', 'postgres']
    conn = psycopg2.connect(database=conn_details[3], user=conn_details[0],
                            password=conn_details[1], host=conn_details[2], port="5432")
    cur = conn.cursor()
    
    # build the sql query we need:
        #get specific battery id
        
    sql_query = 'select *  FROM parsed_data_bess​."Pack_Timeseries" where battery_pack_id='+battery_pack_id+' ;'
        #get all data
    print('sql_query - 1 : ', sql_query)
    
    # run the query (can take a while) and bring the results into a dataframe:
    df = pd.read_sql(sql_query, conn)   
    sql_query2 = 'select *  FROM calculated_data."calculate_data_SOH_bess" where battery_pack_id='+battery_pack_id+' ;'
    print('sql_query - 2: ', sql_query2)
    df2 = pd.read_sql(sql_query2, conn)   
    # columns_names=df.columns
    # close the inbound connection:
    conn.close()
    return df,df2#,df_bat_details
df_temp_list=[]
df_temp_list2=[]
for battery_pack_id in range(501,507):
    print(battery_pack_id)    
    df_temp,df_temp2=load_Data_from_sql(str(battery_pack_id))
    df_temp_list.append(df_temp)
    df_temp_list2.append(df_temp2)
    
df_all=pd.concat(df_temp_list, ignore_index=True)
df_all_SOH_cal=pd.concat(df_temp_list2, ignore_index=True)
#df_all.columns
 # In[ ]: load data
df_specs=pd.read_csv(r'C:\Users\PanagiotisErodotou\OneDrive - Altelium\Documents\Python Scripts\Altelium_codes\CE\dashboard_bess_fake\bess_specs.csv.csv',index_col=None)
df_health=pd.read_csv(r'C:\Users\PanagiotisErodotou\OneDrive - Altelium\Documents\Python Scripts\Altelium_codes\CE\dashboard_bess_fake\battery_health.csv',index_col=None)
df_usage=pd.read_csv(r'C:\Users\PanagiotisErodotou\OneDrive - Altelium\Documents\Python Scripts\Altelium_codes\CE\dashboard_bess_fake\Battery_Usage_Summary​.csv')
# df_all=pd.read_csv(r'C:\Users\PanagiotisErodotou\OneDrive - Altelium\Documents\Python Scripts\Altelium_codes\CE\dashboard_bess_fake\df_all.csv')
# df_all.to_csv(r'C:\Users\PanagiotisErodotou\OneDrive - Altelium\Documents\Python Scripts\Altelium_codes\CE\dashboard_bess_fake\df_all.csv')
# print('get min and max and group by id took : ',str((time.time() - start_time)/60)+'minutes')
    # In[ ]: START
def create_soc_categories(step):
    df_all_small=df_all[['battery_pack_id','pack_soc_percent']]
    df_all_small['SOC Categories']=pd.cut(df_all_small["pack_soc_percent"],np.arange(0, 101, step))
    
    df_all_soc_grouped =  df_all_small.groupby(['battery_pack_id','SOC Categories'],as_index=False).count()
    df_all_soc_grouped.replace(',', '-', regex=True)
    df_all_soc_grouped['SOC Categories'] = df_all_soc_grouped['SOC Categories'].astype(str)
    df_all_soc_grouped=df_all_soc_grouped.replace(',', '% -', regex=True).replace(']', '%)', regex=True)
    
    return df_all_soc_grouped


    # In[ ]: START




st.sidebar.image(r"C:\Users\PanagiotisErodotou\OneDrive - Altelium\Downloads\logo.svg", use_column_width=True)
page = st.sidebar.selectbox('Select page',
  ['Overview','BESS data','Pack data',"Bonus page"])

if page == 'Overview':
    col1, col2,col3 = st.columns([2,10,3])
    col2.title("Welcome to BESS Dashboard!")
    f = open(r"C:\Users\PanagiotisErodotou\OneDrive - Altelium\Downloads\battery-svgrepo-com (7).svg","r")
    lines = f.readlines()
    line_string=''.join(lines)    
    # col2.image(r"C:\Users\PanagiotisErodotou\OneDrive - Altelium\Downloads\battery-svgrepo-com (7).svg", width=60)
    col1.write(line_string, unsafe_allow_html=True, width=60,height=30)
    
        
    # st.title("Welcome to BESS Dashboard!")
    st.markdown("### Health overview​")
    col1, col2, col3,col4 = st.columns(4)
    col1.metric("Battery health", "97 %", "+1.2 %")
    col2.metric("Thermal stability", "73 %", "-8%")
    col3.metric("Fire risk", "15%", "3%")
    col4.metric("Gas alert", "False")

    st.markdown("### BESS Info and Specs")
    
    st.table(df_specs.assign(hack='').set_index('hack'))
    
    st.markdown("### Usage Overview")
    
    st.table(df_usage.reset_index(drop=True).assign(hack='').set_index('hack'))
    
    st.markdown("### Throughput Overview")
    fig = px.bar(df_all_SOH_cal, x='battery_pack_id', y='throughput_value')
    st.plotly_chart(fig,use_container_width = True, width=900)
    
    st.markdown("### SOC Overview")
    step = st.select_slider(
     'Select a step size for the SOC categories',
     options=['5%', '10%', '15%', '20%', '25%', '30%', '35%', '40%', '45%', '50%'])
    
    df_all_soc_grouped=create_soc_categories(int(step.replace('%','')))
    
        
    fig = px.bar(df_all_soc_grouped, x="battery_pack_id", y="pack_soc_percent", color="SOC Categories",
             barmode = 'stack',
                     labels={
                     "battery_pack_id": "Battery Pack ID",
                     "pack_soc_percent": "Pack SOC Count",
                     "SOC Categories": "SOC Range"
                 },)
    st.plotly_chart(fig,use_container_width = True, width=900)
    
    st.markdown("### Battery Packs Health")
    
    st.table(df_health.assign(hack='').set_index('hack'))
    

    
if page == 'Pack data':
    
  st.markdown("### Pack Monitor") 
  num_yrs = st.slider('Select number of days', min_value=1, max_value=580)
  df=df_all.iloc[-num_yrs*60*24:]
  clist = df_all['battery_pack_id'].unique()
  battery_pack_id = st.selectbox("Select a Battery ID:",clist)
  #col1, col2, col3 = st.columns(3)
  #col1 = st.columns(1)
  st.write("Max Temperature")
  fig = px.line(df[df['battery_pack_id'] == battery_pack_id], 
    x = "timestamp_utc", y = "max_pack_temp_deg_c",title = "Max Temperature") 
  st.plotly_chart(fig,use_container_width = True, width=900)
  
  st.write("Max Cell Voltage")
  fig = px.line(df[df['battery_pack_id'] == battery_pack_id], 
    x = "timestamp_utc", y = "max_cell_voltage_v",title = "Max Cell Voltage")
  st.plotly_chart(fig,use_container_width = True)
  
  st.write("Pack Current")
  fig = px.line(df[df['battery_pack_id'] == battery_pack_id], 
    x = "timestamp_utc", y = "pack_current_amp",title = "Max Cell Voltage")
  
  st.plotly_chart(fig,use_container_width = True)
        
if page == 'BESS data':
    st.markdown("### BESS Monitor") 
    num_yrs = st.slider('Select number of days', min_value=1, max_value=580)
    
    df=df_all.iloc[-num_yrs*60*24:]
    
    fig = px.line(df, 
    x = "timestamp_utc", y = "max_pack_temp_deg_c",
    title = "Max Temperature",color = 'battery_pack_id')
  
    st.plotly_chart(fig,use_container_width = True, width=900)
    
    fig = px.line(df, 
    x = "timestamp_utc", y = "max_cell_voltage_v",
    title = "Max Cell Voltage",color = 'battery_pack_id')
    st.plotly_chart(fig,use_container_width = True, width=900)
    
    fig = px.line(df, 
    x = "timestamp_utc", y = "pack_current_amp",
    title = "Current",color = 'battery_pack_id')
    st.plotly_chart(fig,use_container_width = True, width=900)

if page=="Bonus page":
    st.balloons()
    st.markdown("### Thanks for visiting BESS Dashboard!") 
    
    f = open(r"C:\Users\PanagiotisErodotou\OneDrive - Altelium\Downloads\battery-svgrepo-com (6).svg","r")
    lines = f.readlines()
    line_string=''.join(lines)  
    
    col1, col2,col3 = st.columns([10,15,10])

    col2.write(line_string, unsafe_allow_html=True, width=60,height=30)





































