import streamlit as st
import pandas as pd
import os
from datetime import date
import math
import plotly.graph_objects as go
import numpy as np

#-------------------------------------------------Time Tracker---------------------------------------------------------
def interface():
    setup_config = {"Data required":True,
                    "Args":["Database","Email"]}
    return setup_config

def run(*args):
    db = args[0][0]
    email = args[0][1]
    st.header('Time Tracker')
    st.markdown('####')
    timer = st.columns(2)
    dic=db.collection('Users').document(email).collection('PLUGINS').document('TimeTracker').get().to_dict()
    makingdf = {'Date':dic.keys(),'Productive Time':dic.values()}
    df = pd.DataFrame(makingdf).set_index('Date')
    with timer[0].form('timer'):
        st.number_input('Productive Hours', key='hrs')
        def update_timer():
            db.collection('Users').document(email).collection('PLUGINS').document('TimeTracker').update({
                str(date.today()):round(st.session_state.hrs,2)
            })
        st.form_submit_button('Done', on_click=update_timer)
    timer[1].table(df.tail(3))
    if len(df)>0:
        tm = pd.date_range(df.index[0],df.index[-1])
        idx = pd.DatetimeIndex(tm).astype(str)
        df=df.reindex(idx).fillna(0)
        time_lst=[math.floor(i)*60+round((i-math.floor(i))*100) for i in df['Productive Time']]
        text = ['{} Hours {} minutes'.format(math.floor(i/60),i%60) for i in time_lst]
        avg=[]
        if len(df)>4:
            for i in range(4,len(time_lst)):
                avg.append(int(np.array(time_lst[i-4:i+1]).mean()))
            for i in range(4):
                avg.insert(0,avg[0])
            avg_text = ['{} Hours {} minutes'.format(math.floor(i/60),i%60) for i in avg]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index,y=time_lst,fill='tozeroy',name='Time',hovertemplate = '<i>%{text}</i>',text = text))
        if len(df)>4:
            fig.add_trace(go.Scatter(x=df.index,y=avg,fill='tozeroy',name='Average',hovertemplate = '<i>%{text}</i>',text = avg_text))
        fig.update_layout(xaxis_title="Date",yaxis_title="Minutes",title='Daily Productive Hours')
        fig.update_xaxes(showline=True, linewidth=2, linecolor='black', gridcolor='black')
        fig.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='black')
        st.plotly_chart(fig,use_container_width=True)
    
def make_templete(db,email):
    template={}
    plugin_list = db.collection('Users').document(email).collection('PLUGINS').get()
    plugin_list = [i.id for i in plugin_list]
    if 'TimeTracker' not in plugin_list:
        db.collection('Users').document(email).collection('PLUGINS').document('TimeTracker').set(template)
    return