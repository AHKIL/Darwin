from email.policy import default
from multiprocessing.sharedctypes import Value
import streamlit as st
from st_btn_select import st_btn_select
import numpy as np
import pandas as pd
import statistics
import plotly.graph_objects as go
import plotly.express as px
import urllib
import bs4 as bs
import ssl
import re
import requests
from datetime import date
from firebase_admin import firestore
from PLUGINS.Bayes_Theorem import run as Bayes_theoram
from PLUGINS.Hamiltons_Rule import run as Hamiltons_rule
from PLUGINS.Discounted_cash_flow import run as dcf

#-------------------------------------------------Investing Checklist---------------------------------------------------------
def interface():
    setup_config = {"Data required":False,
                    "Args":["Status","Database","Email"]}
    return setup_config
    
def run(*args):
    status = args[0][0]
    db = args[0][1]
    email = args[0][2]
    def plot_aoi(df,dfb,dfc,gross_margin,margins,Payout_Ratio):
        if len(df.columns)==len(dfb.columns) and len(dfb.columns)==len(dfc.columns):
            CFO=np.array(dfc.iloc[0].astype(float))
            interest=np.array(df.iloc[9].astype(float))
            PPE=np.array(dfb.iloc[6].astype(float))
            FCF=CFO-interest-np.concatenate([[0],np.diff(PPE)])
            FCF=(pd.DataFrame({'FCF' : FCF},index=dfc.columns)).transpose()
            dfc = (pd.concat([dfc,FCF]))

        stats = pd.DataFrame({'Gross margin':gross_margin,'EBITDA margin':margins[0],'EBIT margin':margins[1],'EBT margin':margins[2],'Net margin':margins[3],'Payout ratio':Payout_Ratio})
        stats=stats.transpose()
        stats.columns=df.columns
        st.write(stats)
        margins_name=['Mean EBITDA margin','Mean EBIT margin','Mean EBT margin','Mean Net margin']
        margin_col = st.columns(4)
        for j,k,l in zip(margins,margins_name,margin_col):
            meann=statistics.mean([float(i.replace('%','')) for i in j][-5:])
            with l:
                st.write(k,round(meann,2),'%')
        meann=statistics.mean([float(i.replace('%','')) for i in Payout_Ratio][-5:])
        st.write('Mean Payout ratio : ',round(meann,2),'%')
        st.write('Revenue Growth rate : ',round(((df.iloc[0].astype(float)[-1]/df.iloc[0].astype(float)[0])**(1/(len(df.columns)-1))-1)*100,2),'%')
        
#-------------------------------------------------Bar chart------------------------------------------------------
        fig = go.Figure()
        for i in range(len(df)):
            if i==12:
                fig.add_trace(go.Bar(x=df.iloc[i].index,y=df.iloc[i].astype(float),name=df.iloc[i].name))
                continue
            fig.add_trace(go.Bar(x=df.iloc[i].index,y=df.iloc[i].astype(float),name=df.iloc[i].name, visible = "legendonly"))
        for i in range(len(dfb)):
            fig.add_trace(go.Bar(x=dfb.iloc[i].index,y=dfb.iloc[i].astype(float),name=dfb.iloc[i].name, visible = "legendonly"))
        for i in range(len(dfc)):
            fig.add_trace(go.Bar(x=dfc.iloc[i].index,y=dfc.iloc[i].astype(float),name=dfc.iloc[i].name, visible = "legendonly"))
        fig.update_layout(xaxis_title="Financial Year",yaxis_title="Numbers in ₹ cr",title='Financial Statement',
                         plot_bgcolor='rgba(0, 0, 0, 0)',paper_bgcolor='rgba(0, 0, 0, 0)',margin_b=50)
        fig.update_xaxes(showline=True, linewidth=1, linecolor='black', gridcolor='black')
        fig.update_yaxes(showline=True, linewidth=1, linecolor='black', gridcolor='black')
        st.plotly_chart(fig,use_container_width=True)

#-------------------------------------------------Arithmetic------------------------------------------------------
        with st.expander('Arithmetic'):
            rows = st.number_input('No of rows',min_value=1)
            fin_state, row_slt = st.columns(2)
            fin_statement = fin_state.selectbox('Financial Statement', ['Income Statement','Balance Sheet','Cash Flow Statement'])
            if fin_statement == 'Income Statement':
                r_i = row_slt.selectbox('Row',list(df.index))
                selected_rows= df.loc[r_i]
            if fin_statement == 'Balance Sheet':
                r_i = row_slt.selectbox('Row',list(dfb.index))
                selected_rows= dfb.loc[r_i]
            if fin_statement == 'Cash Flow Statement':
                r_i = row_slt.selectbox('Row',list(dfc.index))
                selected_rows= dfc.loc[r_i]

            if rows==1:
                opr = st.selectbox('Operation', ['Compound Add + '],key=f's_r_')
                if opr == 'Compound Add + ':
                    cum_arr = [float(selected_rows[0])]
                    for i in selected_rows[1:]:
                        cum_arr.append(float(i)+cum_arr[-1])
                    y=cum_arr
            if rows>1:
                selected_rows = np.array(selected_rows).astype('float64')
                for i in range(1,rows):
                    opr = st.selectbox('Operation', ['Add +','Substract -','Multiply *','Divide /'],key=f's_r_{i}')
                    fin_state, row_slt = st.columns(2)
                    fin_statement = fin_state.selectbox('Financial Statement', ['Income Statement','Balance Sheet','Cash Flow Statement'],key=f'f_s_{i}')
                    if fin_statement == 'Income Statement':
                        r_i = row_slt.selectbox('Row',list(df.index),key=f'i_s_{i}')
                        if opr == 'Add +':
                            selected_rows = selected_rows+np.array(df.loc[r_i]).astype('float64')
                        if opr == 'Substract -':
                            selected_rows = selected_rows-np.array(df.loc[r_i]).astype('float64')
                        if opr == 'Multiply *':
                            selected_rows = selected_rows*np.array(df.loc[r_i]).astype('float64')
                        if opr == 'Divide /':
                            selected_rows = selected_rows/np.array(df.loc[r_i]).astype('float64')
                    if fin_statement == 'Balance Sheet':
                        r_i = row_slt.selectbox('Row',list(dfb.index),key=f'b_s_{i}')
                        if opr == 'Add +':
                            selected_rows = selected_rows+np.array(dfb.loc[r_i]).astype('float64')
                        if opr == 'Substract -':
                            selected_rows = selected_rows-np.array(dfb.loc[r_i]).astype('float64')
                        if opr == 'Multiply *':
                            selected_rows = selected_rows*np.array(dfb.loc[r_i]).astype('float64')
                        if opr == 'Divide /':
                            selected_rows = selected_rows/np.array(dfb.loc[r_i]).astype('float64')
                    if fin_statement == 'Cash Flow Statement':
                        r_i = row_slt.selectbox('Row',list(dfc.index),key=f'c_s_{i}')
                        if opr == 'Add +':
                            selected_rows = selected_rows+np.array(dfc.loc[r_i]).astype('float64')
                        if opr == 'Substract -':
                            selected_rows = selected_rows-np.array(dfc.loc[r_i]).astype('float64')
                        if opr == 'Multiply *':
                            selected_rows = selected_rows*np.array(dfc.loc[r_i]).astype('float64')
                        if opr == 'Divide /':
                            selected_rows = selected_rows/np.array(dfc.loc[r_i]).astype('float64')
                    y=selected_rows
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.columns,y=y))
            fig.update_layout(xaxis_title="Date",yaxis_title="Value (in cr)")
            fig.update_xaxes(showline=True, linewidth=2, linecolor='black', gridcolor='black')
            fig.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='black')
            st.plotly_chart(fig,use_container_width=True)

#-------------------------------------------------sunburst 1------------------------------------------------------   
        year = st.select_slider('Year',df.columns,value=df.columns[-1])
        sunburst1,sunburst2=st.columns(2)     
        child = ['Raw Materials','Power & Fuel Cost','Employee Cost','Selling & Administrative Expenses',
                 'Operating & Other expenses',None,None,None]
        parent =['COGS','COGS','Operating costs','Operating costs','Operating costs','Depreciation/Amortization',
                 'Interest & Other Items','Taxes & Other Items']
        region =['Costs Breakup']*8
        values=list(df[year][1:3].values)
        values.extend(list(df[year][3:6].values))
        values.append(df[year][7])
        values.append(df[year][9])
        values.append(df[year][11])
        for i in range(len(values)):
            values[i]=float(values[i])
            if values[i]<0:
                st.warning('warning negative values excluded from Costs Breakup')
                values[i]=0
        new_df = pd.DataFrame(dict(child=child, parent=parent, region=region, values=values))
        fig = px.sunburst(new_df, path=['region','parent','child'], values='values')
        fig.update_traces(go.Sunburst(hovertemplate='Label : %{label}<br>Value : %{value}<br>Percentage : %{percentEntry:.2%}'))
        fig.update_traces(textinfo="label+percent entry",textfont=dict(color='White'))
        sunburst1.plotly_chart(fig,use_container_width=True)

#-------------------------------------------------sunburst 2------------------------------------------------------        
        outer_most=['Cash and Short Term Investments','Total Receivables','Total Inventory','Other Current Assets',
                    'Loans & Advances','Net Property/Plant/Equipment','Goodwill & Intangibles','Long Term Investments','Deferred Tax Assets (Net)','Other Assets',
                    'Accounts Payable','Total Deposits','Other Current Liabilities',
                    'Total Long Term Debt','Deferred Tax Liabilities (Net)','Other Liabilities',
                    None,None,None,None,None]
        between =['Current Assets','Current Assets','Current Assets','Current Assets',
                  'Non Current Assets','Non Current Assets','Non Current Assets','Non Current Assets','Non Current Assets','Non Current Assets',
                  'Current Liabilities','Current Liabilities','Current Liabilities',
                  'Non Current Liabilities','Non Current Liabilities','Non Current Liabilities',
                  'Common Stock','Additional Paid-in Capital','Reserves & Surplus','Minority Interest','Other Equity']
        inner_most=['Total Assets','Total Assets','Total Assets','Total Assets','Total Assets','Total Assets','Total Assets','Total Assets','Total Assets','Total Assets',
                    'Total Liabilities','Total Liabilities','Total Liabilities','Total Liabilities','Total Liabilities','Total Liabilities',
                    'Total Equity','Total Equity','Total Equity','Total Equity','Total Equity']
        nf=dfb.drop(index=['Current Assets','Non Current Assets','Current Liabilities','Non Current Liabilities',
                          'Total Assets','Total Liabilities','Total Equity',
                          "Total Liabilities & Shareholder's Equity",'Total Common Shares Outstanding'])
        
        if year in nf.columns.to_list():
            values = nf[year].values
            for i in range(len(values)):
                values[i]=float(values[i])
                if values[i]<0:
                    st.warning('warning negative values excluded from Balance Sheet')
                    values[i]=0
            new_df = pd.DataFrame(dict(outer_most=outer_most, between=between, inner_most=inner_most, values=values))
            fig = px.sunburst(new_df, path=['inner_most','between','outer_most'], values='values')
            fig.update_traces(go.Sunburst(hovertemplate='Label : %{label}<br>Value : %{value}<br>Percentage : %{percentEntry:.2%}'))
            fig.update_traces(textinfo="label+percent entry",textfont=dict(color='White'))
            sunburst2.plotly_chart(fig,use_container_width=True)
        else:
            sunburst2.warning('Balance sheet not found')
    
    @st.cache
    def comp_fund_data_extractor(l):
        ssl._create_default_https_context = ssl._create_unverified_context
        t=l.find('/',l.find('/',l.find('/',l.find('/')+1)+1)+1)+1
        if l.find('/',t)!=-1:
            indx=l.find('/',t)
        if l.find('/',t)==-1:
            indx=l.find('?',t)
        if indx==-1:
            indx=len(l)
        income=l[0:indx]+'/financials?period=annual&statement=income&view=normal'
        balance=l[0:indx]+'/financials?period=annual&statement=balancesheet&view=normal'
        cashflow=l[0:indx]+'/financials?period=annual&statement=cashflow'
        urlpage=urllib.request.urlopen(income)
        soup=bs.BeautifulSoup(urlpage,'html.parser')
        links=[]
        for link in soup.findAll('a'):
            anuallinks = link.get('href')
            if anuallinks is not None and anuallinks.find('bseindia')!=-1:
                links.append(anuallinks)
        coulmn=[]
        dta=[]
        coulmn.append(' ')
        for i in soup.find('div',{'class':re.compile(r'financials-table relative')}).findAll('span'):
            if 'span' in str(i.contents) or str(i.text)=='' or  str(i.text)=='See Costs':
                continue
            if 'FY' in str(i.text):
                dta.append(coulmn)
                coulmn=[]
            coulmn.append(i.text.replace(',', '').replace('—', '0'))
        dta.append(coulmn)
        df = pd.DataFrame(dta)
        df=df.set_index([0]).transpose().set_index([' '])
        
        urlpage=urllib.request.urlopen(balance)
        soup=bs.BeautifulSoup(urlpage,'html.parser')
        coulmn=[]
        dta=[]
        coulmn.append(' ')
        for i in soup.find('div',{'class':re.compile(r'financials-table relative')}).findAll('span'):
            if 'span' in str(i.contents) or str(i.text)=='' or  str(i.text)=='See Costs':
                continue
            if 'FY' in str(i.text):
                dta.append(coulmn)
                coulmn=[]
            coulmn.append(i.text.replace(',', '').replace('—', '0'))
        dta.append(coulmn)
        dfb = pd.DataFrame(dta)
        dfb=dfb.set_index([0]).transpose().set_index([' '])
        dfb=dfb[:-1]

        urlpage=urllib.request.urlopen(cashflow)
        soup=bs.BeautifulSoup(urlpage,'html.parser')
        coulmn=[]
        dta=[]
        coulmn.append(' ')
        for i in soup.find('div',{'class':re.compile(r'financials-table relative')}).findAll('span'):
            if 'span' in str(i.contents) or str(i.text)=='' or  str(i.text)=='See Costs':
                continue
            if 'FY' in str(i.text):
                dta.append(coulmn)
                coulmn=[]
            coulmn.append(i.text.replace(',', '').replace('—', '0'))
        dta.append(coulmn)
        dfc = pd.DataFrame(dta)
        dfc=dfc.set_index([0]).transpose().set_index([' '])
        dfc=dfc[:-1]
        urlpage.close()
        
        response = requests.get(l[0:indx])
        soup = bs.BeautifulSoup(response.text, features="html.parser")
        t=soup.find('div',{'class':re.compile(r'quote-box-root with-children')}).findAll('span')[0]
        c_price=t.text
        t=soup.find('div',{'data-label-key':'marketCap'}).findAll('span')[1]
        c_mcap=t.text
        urlpage.close()
        if float(dfc.loc['Free Cash Flow'][-1]) > 0 and float(dfc.loc['Free Cash Flow'][0]) > 0 :
            FCF_grw=round((((float(dfc.loc['Free Cash Flow'][-1])/float(dfc.loc['Free Cash Flow'][0]))**(1/(len(dfc.columns)-1)))-1)*100,2)
        else:
            FCF_grw='Unable to calculate'
        gross_margin=[str(i) + '%' for i in list(round((df.iloc[0].astype(float)-(df.iloc[1].astype(float)+df.iloc[2].astype(float)))*100/df.iloc[0].astype(float),2))]
        margins=[]
        for j in [6,8,10,12]:
            margins.append([str(i)+'%' for i in np.around(df.iloc[j].values.astype(float)/df.iloc[0].values.astype(float)*100, decimals = 2)])
        Payout_Ratio=[str(round(i*100))+'%' for i in df.iloc[15].values.astype(float)]
        return df,dfb,dfc,gross_margin,margins,Payout_Ratio,c_price,c_mcap,FCF_grw,links

    st.header('Investing Checklist')
    st.markdown('####')
    if 'count' not in st.session_state:
        st.session_state['count']=0
    #-----------------------------------------Select or create new company-----------------------------------------------------
    slct,new = st.columns([8.2,1.8])
    all_comp = db.collection('Users').document(email).collection('PLUGINS').document('Chechlist').collection('CompanyList')
    all_comp_data = all_comp.get()
    all_comp_list = [i.id for i in all_comp_data]
    selected_comp = slct.selectbox('Select company',all_comp_list)

    def creat_new_company():
        dic = {'Name':'','Link':'','Notes':'','Revenue_breakup':{}
                                            ,'Sectors outlooks':'','Management':{'Manager and his track record':''
                                                            ,'Managers net worth is linked with the company':''
                                                            ,'Is the manager the owner and level 5 leader':''}
                                            ,'Leverage and failure':'','Motes and competitive advantage':''
                                            ,'Probabilities':{},'DCF Hamiltons formula':'','What can go wrong and max loss':''}
        for i in range(11):
            dic['Revenue_breakup'][str(date.today().year-i)]={'Revenue_from_operations':{},'Other_renenue_sources':{}}
        all_comp.document('Name').set(dic)

    new.title('')
    new.button('Create new analysis',on_click=creat_new_company)

    if len(all_comp_list)>0:
        comp_json_data = all_comp_data[all_comp_list.index(selected_comp)].to_dict()
        def nextup():
            if st.session_state['count']!=len(comp_json_data)-3:
                st.session_state['count']+=1
        def backup():
            if st.session_state['count']!=0:
                st.session_state['count']-=1

        hdr, hide_show = st.columns([8,1.5])
        hdr.write('---')
        if status==':seedling:'+' Online':
            with hide_show.container():
                hd_sh = st_btn_select(('Hide', 'Show'))
            if comp_json_data['Link']!='':
                df,dfb,dfc,gross_margin,margins,Payout_Ratio,c_price,c_mcap,FCF_grw,links = comp_fund_data_extractor(comp_json_data['Link'])
                if hd_sh=='Show':
                    st.write('Share price : ',c_price)
                    st.write(c_mcap)
                    st.write('Free Cash Flow growth : ',FCF_grw,'%')
                    plot_aoi(df,dfb,dfc,gross_margin,margins,Payout_Ratio)
                    
        st.subheader('Checklist items')
        st.markdown('####')
        #-------------------------------------------------Checklist items---------------------------------------------------------
        if st.session_state['count']==0:
            arr = st.columns([1,2]) 
            def rename_comp():
                all_comp.document(comp_json_data['Name']).delete()
                comp_json_data['Name']=st.session_state.cmpr
                all_comp.document(st.session_state.cmpr).set(comp_json_data)
            def edit_link():
                all_comp.document(selected_comp).update({'Link':st.session_state.ttl})
            def edit_notes():
                all_comp.document(selected_comp).update({'Notes':st.session_state.checklist_notes})
            comp_json_data['Name'] = arr[0].text_input('Rename',value = selected_comp,on_change=rename_comp,key='cmpr')
            comp_json_data['Link'] = arr[0].text_input('Ticker Tape Link',value = comp_json_data['Link'], on_change=edit_link, key='ttl' )
            if comp_json_data['Link']!='':
                with arr[0].expander('Annual reports'):
                    df,dfb,dfc,gross_margin,margins,Payout_Ratio,c_price,c_mcap,FCF_grw,links = comp_fund_data_extractor(comp_json_data['Link'])
                    for i,j in zip(links,df.columns[-len(links):]):
                        st.write(f"[Annual Report {j}]({i})")
            arr[0].title('')
            arr[0].slider('Notes height', min_value=350, max_value=1000, value=350, step=10, key='note_size')
            comp_json_data['Notes'] = arr[1].text_area('General Notes',placeholder='Enter Note',
                                                        height=st.session_state.note_size,value = comp_json_data['Notes'], 
                                                        on_change=edit_notes, key='checklist_notes' )
        if st.session_state['count']==1:
            Sour,Breakup,=st.columns(2)
            f_in,yr_slt=st.columns(2)
            ytbinc=[]
            for tobinc in comp_json_data['Revenue_breakup']:
                if len(comp_json_data['Revenue_breakup'][tobinc]['Revenue_from_operations'])!=0:
                    ytbinc.append(int(tobinc))
            if len(ytbinc)==0:
                ytbinc.append(date.today().year-1)
            inc_year = yr_slt.multiselect('Include Year',list(range(date.today().year-10, date.today().year+1)),default=ytbinc)
            inc_year = sorted(inc_year ,reverse=True)
            cur_yr = str(yr_slt.selectbox('Current Year',inc_year))
            if len(inc_year)==0:
                return
            st.write('---')
            dvid = st.columns([1,1,1])
            def click_Sour_button():
                if st.session_state.rev_sour=='':
                    return
                st.session_state.rev_sour=''
                all_comp.document(selected_comp).update({f'Revenue_breakup.{cur_yr}.{st.session_state.rev_sour}':{}})
            Sour.text_input('Revenue Source',key='rev_sour', on_change=click_Sour_button)
            kys1=list(comp_json_data['Revenue_breakup'][cur_yr].keys())
            kys1.sort(reverse=True)
            rad1io = dvid[0].radio('Revenue Source',kys1, format_func = lambda x: x.replace('_',' '))

            def process_fast_input():
                if st.session_state[rad1io]!='':
                    raw_data = st.session_state[rad1io]
                    raw_data = raw_data.replace(',','')
                    count = 0
                    year1 = []
                    year2 = []
                    name = []
                    name.append('')
                    for i in raw_data.split():
                        if i.replace('.','').isdigit() and count == 0:
                            count = count+1
                            year1.append(i)
                        elif count == 1:
                            count = count+1
                            year2.append(i)
                            name.append('')
                        else : 
                            name[-1]+=' '+i
                            count = 0
                    cm_df = pd.DataFrame({'name':name[:-1],'Year 1':year1,'Year 2':year2})
                    for n,v in zip(cm_df['name'],cm_df['Year 1']):
                        comp_json_data['Revenue_breakup'][cur_yr][rad1io][n]=v
                    all_comp.document(selected_comp).update({f'Revenue_breakup.{cur_yr}.{rad1io}':comp_json_data['Revenue_breakup'][cur_yr][rad1io]})
                    st.session_state[rad1io]=''

            f_in.text_area('Fast input',key=rad1io,height=140, on_change=process_fast_input)

            def del_Sour():
                all_comp.document(selected_comp).update({f'Revenue_breakup.{cur_yr}.{rad1io}':firestore.DELETE_FIELD})
            def rename_Sour():
                all_comp.document(selected_comp).update({f'Revenue_breakup.{cur_yr}.{rad1io}':firestore.DELETE_FIELD})
                all_comp.document(selected_comp).update({f'Revenue_breakup.{cur_yr}.{st.session_state.fac_}':comp_json_data['Revenue_breakup'][cur_yr][rad1io]})
            dvid[0].text_input('Rename',key='fac_',value=rad1io,on_change=rename_Sour)
            dvid[0].button('Delete',key='fac',on_click = del_Sour)  
            def click_Break_button_():
                if st.session_state.rev_brek_=='':
                    return
                all_comp.document(selected_comp).update({f'Revenue_breakup.{cur_yr}.{rad1io}.{st.session_state.rev_brek_}':''})
                st.session_state.rev_brek_=''
            Breakup.text_input('Revenue_Breakup',key='rev_brek_', on_change=click_Break_button_)
            kys2=list(comp_json_data['Revenue_breakup'][cur_yr][rad1io].keys())
            if len(kys2)!=0: 
                kys2.sort()
                rad2=dvid[1].radio('Revenue_Breakup',kys2)
                def del_Breakup():
                    all_comp.document(selected_comp).update({f'Revenue_breakup.{cur_yr}.{rad1io}.{rad2}':firestore.DELETE_FIELD})
                def rename_Breakup():
                    all_comp.document(selected_comp).update({f'Revenue_breakup.{cur_yr}.{rad1io}.{rad2}':firestore.DELETE_FIELD})
                    all_comp.document(selected_comp).update({f'Revenue_breakup.{cur_yr}.{rad1io}.{st.session_state.breakup_}':comp_json_data['Revenue_breakup'][cur_yr][rad1io][rad2]})
                dvid[1].text_input('Rename',key='breakup_',value=rad2,on_change=rename_Breakup)
                dvid[1].button('Delete',key='Breakup',on_click = del_Breakup)
                def enter_income():
                    all_comp.document(selected_comp).update({f'Revenue_breakup.{cur_yr}.{rad1io}.{rad2}':st.session_state[rad1io+rad2+'c']})
                dvid[2].text_input('Income',key=rad1io+rad2+'c',value=comp_json_data['Revenue_breakup'][cur_yr][rad1io][rad2],on_change=enter_income)
            no_col=2
            size=int(len(inc_year)/no_col)
            for yyyinc in range(size):
                arr_yync=st.columns(no_col)
                for not_used in range(no_col):
                    parent=[]
                    child =[]
                    values =[]
                    for i in comp_json_data['Revenue_breakup'][str(inc_year[yyyinc*no_col+not_used])].keys():
                        for j in comp_json_data['Revenue_breakup'][str(inc_year[yyyinc*no_col+not_used])][i]:
                            parent.append(i)
                            child.append(j)
                            if comp_json_data['Revenue_breakup'][str(inc_year[yyyinc*no_col+not_used])][i][j]!='':
                                values.append(float(comp_json_data['Revenue_breakup'][str(inc_year[yyyinc*no_col+not_used])][i][j].replace(',','')))
                    region =[f'Rev. Breakup {str(inc_year[yyyinc*no_col+not_used])}']*len(child)
                    if len(values)>0 and len(child)==len(values):
                        new_df = pd.DataFrame({'child':child, 'parent':parent, 'region':region, 'values':values})
                        fig = px.sunburst(new_df, path=['region','parent','child'], values='values')
                        fig.update_traces(go.Sunburst(hovertemplate='Label : %{label}<br>Value : %{value}<br>Percentage : %{percentEntry:.2%}'))
                        fig.update_traces(textinfo="label+percent entry",textfont=dict(color='White'))
                        arr_yync[not_used].plotly_chart(fig,use_container_width=True)

            arr_yync=st.columns(no_col)
            for yyyinc in range(len(inc_year)%no_col):
                parent=[]
                child =[]
                values =[]
                for i in comp_json_data['Revenue_breakup'][str(inc_year[(size*no_col)+yyyinc])].keys():
                    for j in comp_json_data['Revenue_breakup'][str(inc_year[(size*no_col)+yyyinc])][i]:
                        parent.append(i)
                        child.append(j)
                        if comp_json_data['Revenue_breakup'][str(inc_year[(size*no_col)+yyyinc])][i][j]!='':
                            values.append(float(comp_json_data['Revenue_breakup'][str(inc_year[(size*no_col)+yyyinc])][i][j].replace(',','')))
                region =[f'Rev. Breakup {str(inc_year[(size*no_col)+yyyinc])}']*len(child)
                if len(values)>0 and len(child)==len(values):
                    new_df = pd.DataFrame({'child':child, 'parent':parent, 'region':region, 'values':values})
                    fig = px.sunburst(new_df, path=['region','parent','child'], values='values')
                    fig.update_traces(go.Sunburst(hovertemplate='Label : %{label}<br>Value : %{value}<br>Percentage : %{percentEntry:.2%}'))
                    fig.update_traces(textinfo="label+percent entry",textfont=dict(color='White'))
                    arr_yync[yyyinc].plotly_chart(fig,use_container_width=True)

            plot_lst_operations={}
            plot_lst_others={}
            for j in inc_year:
                for i in comp_json_data['Revenue_breakup'][str(j)]['Revenue_from_operations']:
                    if i not in plot_lst_operations.keys():
                        plot_lst_operations[i]={'Year':[],'Amount':[]}
                    plot_lst_operations[i]['Year'].append(j)
                    plot_lst_operations[i]['Amount'].append(float(comp_json_data['Revenue_breakup'][str(j)]['Revenue_from_operations'][i]))
                for i in comp_json_data['Revenue_breakup'][str(j)]['Other_renenue_sources']:
                    if i not in plot_lst_others.keys():
                        plot_lst_others[i]={'Year':[],'Amount':[]}
                    plot_lst_others[i]['Year'].append(j)
                    plot_lst_others[i]['Amount'].append(float(comp_json_data['Revenue_breakup'][str(j)]['Other_renenue_sources'][i]))
                    
            fig = go.Figure()
            for i in plot_lst_operations:
                fig.add_trace(go.Bar(x=plot_lst_operations[i]['Year'],y=plot_lst_operations[i]['Amount'],name=i, visible = "legendonly"))
            for i in plot_lst_others:
                fig.add_trace(go.Bar(x=plot_lst_others[i]['Year'],y=plot_lst_others[i]['Amount'],name=i, visible = "legendonly"))
            fig.update_layout(xaxis_title="Financial Year",yaxis_title="Numbers in ₹ cr",title='Revenue_Breakup',
                            plot_bgcolor='rgba(0, 0, 0, 0)',paper_bgcolor='rgba(0, 0, 0, 0)',margin_b=50)
            fig.update_xaxes(showline=True, linewidth=1, linecolor='black', gridcolor='black')
            fig.update_yaxes(showline=True, linewidth=1, linecolor='black', gridcolor='black')
            st.plotly_chart(fig,use_container_width=True)
        if st.session_state['count']==2:
            buffor = st.text_input('• What are the sectors outlooks ?')
            if buffor != '':
                comp_json_data['Sectors outlooks'] = buffor
        if st.session_state['count']==3:
            buffor1 = st.text_input('• Who is the manager/CEO of the company and what is his track record ?')
            if buffor1 != '':
                comp_json_data['Management']['Manager and his track record'] = buffor1
            buffor2 = st.text_input('• What percentage of the managers/CEO net worth is linked with the company ?')
            if buffor2 != '':
                comp_json_data['Management']['Managers net worth is linked with the company'] = buffor2
            buffor3 = st.text_input('• Is the manager/CEO the owner of the business and level 5 leader ie. Integrity . intelligence, experience and dedication ?')
            if buffor3 != '':
                comp_json_data['Management']['Is the manager the owner and level 5 leader'] = buffor3
        if st.session_state['count']==4:
            buffor = st.text_input('• Various types of leverage and failure related to leverage things ?')
            if buffor != '':
                comp_json_data['leverage and failure'] = buffor
        if st.session_state['count']==5:
            buffor = st.text_input('• Motes and competitive advantage shrinking motes or non existing motes ?',value=comp_json_data['Motes and competitive advantage'])        
            if buffor != '':
                comp_json_data['Motes and competitive advantage'] = buffor
        if st.session_state['count']==6:
            st.write('• What is probabilities of the outcome (Bayes theorem) ?')
            fact,fact_b,poss,poss_b=st.columns([2,1,2,1])
            st.write('---')
            divid = st.columns([1,1,2])
            fact_b.title('')
            adf = fact.text_input('Factor')
            if fact_b.button('Add Factor'):
                comp_json_data['Probabilities'][adf]={}
            keys1=list(comp_json_data['Probabilities'].keys())
            if len(keys1)!=0:
                rd1 = divid[0].radio('Factors',keys1)
                def del_fac():
                    del comp_json_data['Probabilities'][rd1]
                ren_fac = divid[0].text_input('Rename',key='fac',value=rd1)
                def rename_fac():
                    comp_json_data['Probabilities'][ren_fac]=comp_json_data['Probabilities'].pop(rd1)
                divid[0].button('Rename',key='fac',on_click=rename_fac)
                divid[0].button('Delete',key='fac',on_click = del_fac)  
                poss_b.title('')
                adp = poss.text_input('Possibility')
                if poss_b.button('Add Possibility'):
                    comp_json_data['Probabilities'][rd1][adp]={'Probability':'','Description':''}
                keys2=list(comp_json_data['Probabilities'][rd1].keys())
                if len(keys2)!=0: 
                    rd2=divid[1].radio('Possibilities',keys2)
                    def del_poss():
                        del comp_json_data['Probabilities'][rd1][rd2]
                    ren_pos = divid[1].text_input('Rename',key='poss',value=rd2)
                    def rename_poss():
                        comp_json_data['Probabilities'][rd1][ren_pos]=comp_json_data['Probabilities'][rd1].pop(rd2)
                    divid[1].button('Rename',key='poss',on_click=rename_poss)
                    divid[1].button('Delete',key='poss',on_click = del_poss)
                    with divid[2].form('fatpinput'+rd1+rd2,True):
                        st.write(rd1+' - '+rd2)
                        comp_json_data['Probabilities'][rd1][rd2]['Probability']=st.text_input('Probability',value=comp_json_data['Probabilities'][rd1][rd2]['Probability'])
                        comp_json_data['Probabilities'][rd1][rd2]['Description']=st.text_area('Description',value=comp_json_data['Probabilities'][rd1][rd2]['Description'])
                        st.form_submit_button('Add')
            Bayes_theoram()
        if st.session_state['count']==7:
            buffor = st.text_input('• What is the net gain from Hamiltons formula ?')
            if buffor != '':
                comp_json_data['DCF Hamiltons formula'] = buffor
            Hamiltons_rule()
            with st.expander('DCF'):
                dcf()
        if st.session_state['count']==8:
            buffor = st.text_input('• What can go wrong and how much drop is possible ?')
            if buffor != '':
                comp_json_data['What can go wrong and max loss'] = buffor
            with st.expander("hamilton's Rule"):
                Hamiltons_rule()
            with st.expander("Bayes theoram"):
                Bayes_theoram()
        if st.session_state['count']==9:
            st.text_input('• Check the database if it is the first company or there are companies in the database ?')

        bc,nx,em= st.columns([1,2,10])
        bc.button('Back', on_click=backup)
        nx.button('Next', on_click=nextup)       
