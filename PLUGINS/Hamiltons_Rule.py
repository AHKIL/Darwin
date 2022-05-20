import streamlit as st
import pandas as pd
from collections import Counter
from itertools import product
import numpy as np

#-------------------------------------------------Discounted cash flow---------------------------------------------------------
def interface():
    setup_config = {"Data required":False,
                    "Args":[]}
    return setup_config

def run(*args):
    st.header('Hamiltons Rule')
    st.markdown('####')
    df=pd.DataFrame({'Name':['Value','Probability']})
    level = st.number_input('No of levels',min_value=1,step=1,help='No of constrains eg Revenue, Net Income')
    opr=[]
    with st.form('Dictionary'):
        try:
            current_price = float(st.text_input('Compare value',placeholder='100',help='Eg Enterprise value'))
        except:
            current_price=1
        for i in range(int(level)):
            if i!=0:
                opr.append(st.text_input('Operation',key='Operation'+str(i),value='*'))
            inpt=st.columns(3)
            nam = inpt[0].text_input('Name',key='Name'+str(i),placeholder='Name')
            val = inpt[1].text_input('Value',key='Value'+str(i),placeholder='1.07,1,.93')
            prb = inpt[2].text_input('Probability',key='Probability'+str(i),placeholder='80,10,10')
            try:
                val = val.split(',')
                prb = prb.split(',')
                prb = [float(j)/100 for j in prb]
                df[nam]=[val,prb]
            except:
                continue
        st.form_submit_button('Compute')
    try : 
        summ=0
        for i in opr:
            co = Counter(i)
            summ+=co['-']+co['*']+co['+']
        df=df.set_index('Name', drop=True)
        operations=df.columns[0]+' '
        for i,j in zip(df.columns[1:],opr):
            operations+=j.replace('*','x')+' '+i+' '
        out_prob=[]
        price=[]
        for element in product(*df.iloc[1]):
            out_prob.append(np.prod(element))
        for element in product(*df.iloc[0]):
            strng = '('*(summ-1)+element[0]
            for k,l in zip(element[1:],opr):
                strng = strng + l+k
            start=strng.find(opr[0][0])+1
            strng = strng[:start]+strng[start:].replace('*',')*').replace('-',')-').replace('+',')+')
            price.append(eval(strng))
        arr={'Probability':out_prob,'Price':price}
        outcome=pd.DataFrame(arr)
        outcome['Probable price']=outcome['Probability']*outcome['Price']
        with st.expander('Probability Distribution'):
            st.table(outcome)
        st.write(operations)
        metr = st.columns([2.4,2.2,.8])
        metr[0].metric(label="Probable intrinsic price", value=round(outcome['Probable price'].sum(),2),delta=str(round((outcome['Probable price'].sum()-current_price)*100/current_price,2))+'%')
        metr[1].metric(label="Best case", value=round(outcome['Price'].max(),2),delta=str(round((outcome['Price'].max()-current_price)*100/current_price,2))+'%')
        metr[2].metric(label="Worst case", value=round(outcome['Price'].min(),2),delta=str(round((outcome['Price'].min()-current_price)*100/current_price,2))+'%')
        for count in range(len(outcome)): 
            if (outcome.loc[outcome['Price']==outcome['Price'].nsmallest(count+1).iloc[-1]]['Probability'].iloc[-1])>0.01:
                st.write('The worst case senario with at least 1% probability is',round(outcome.loc[outcome['Price']==outcome['Price'].nsmallest(count+1).iloc[-1]]['Price'].iloc[-1],2))
                break
    except:
        return