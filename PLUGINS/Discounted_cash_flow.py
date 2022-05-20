import streamlit as st
import datetime 
import numpy as np
import plotly.graph_objects as go

#-------------------------------------------------Discounted cash flow---------------------------------------------------------
def interface():
    setup_config = {"Data required":False,
                    "Args":[]}
    return setup_config

def run(*args):
    st.header('Discounted cash flow')
    st.markdown('####')
    try:
        cf1 = float(st.text_input('This year Free Cash Flow',placeholder='0'))
    except:
        cf1=0
    arr = st.columns(4)
    d=float(arr[0].slider('Discount rate',min_value=1.20,max_value=2.00,step=0.01,value=1.50))
    nmcd=st.columns(4)
    n=int(nmcd[0].number_input('Time period',min_value=1,value=10))
    mcap=float(nmcd[1].text_input('Marketcap',value=0))
    cash=float(nmcd[2].text_input('Cash',value=0))
    debt=float(nmcd[3].text_input('Debt',value=0))
    st.write('Growth rate')
    grw=st.columns(n)
    intrinsic_value=0
    grwt=1
    projected_years = []
    projected_growth = []
    projected_fcf = []
    for i in range(n):
        projected_years.append(f'Year {datetime.date.today().year+i+1}')
        projected_growth.append(float(grw[i].text_input(projected_years[-1],value=1.2)))
        grwt = grwt*projected_growth[-1]
        projected_fcf.append(grwt*cf1)
        if i == n-1:
            pe=float(arr[3].slider('Terminal Value',min_value=10,max_value=15,step=1,value=12))
            grwt = grwt*pe
        intrinsic_value += grwt/(d**(i+1)) 
    st.write('Free Cash flow')
    fcf_p=st.columns(n)
    for j,k in zip(projected_fcf,range(n)):
        fcf_p[k].write(str(round(j,2)))
    for g in np.arange(1,3.0001,.0001):
        x=g/d
        if round(x*((((x**(n-1))-1)/(x-1))+((x**(n-1))*pe)), 2) == round(intrinsic_value,2):
            avg_gwt=g
            flag=0
            break
        else:
            flag=1
    intrinsic_value=intrinsic_value* cf1
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=projected_years,y=projected_growth,name='Actual'))
    if flag==0:
        fig.add_trace(go.Scatter(x=projected_years,y=[round(avg_gwt,2)]*n,name='Average'))
    fig.update_layout(xaxis_title="Financial Year",yaxis_title="Growth rate",title='Growth Rate chart',plot_bgcolor='rgba(0, 0, 0, 0)',paper_bgcolor='rgba(0, 0, 0, 0)',margin_b=0)
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black', gridcolor='black')
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='black' )
    st.plotly_chart(fig,use_container_width=True)
    met=st.columns(3)
    try : 
        met[0].metric(label="Current Enterprise value", value=str(round(mcap-cash+debt,2))+' cr',delta=str(round(((intrinsic_value/(mcap-cash+debt))-1)*100,2))+" %")
    except :
        met[0].metric(label="Current Enterprise value", value=str(round(mcap-cash+debt,2))+' cr')
    met[1].metric(label="Intrinsic Enterprise value", value=str(round(intrinsic_value,2))+' cr')
    met[2].metric(label="Enterprise value with 50% magin of safety", value=str(round(intrinsic_value/2,2))+' cr')
    st.subheader('')
    with st.expander('Disclaimer'):
        st.caption('*The current Enterprise value should be at the Intrinsic Enterprise value to get you returns equal to the discount rate')
