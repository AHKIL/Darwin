import streamlit as st
import folium
from streamlit_folium import folium_static
import branca
from branca.element import Figure
import os

#-------------------------------------------------MAPS---------------------------------------------------------
def interface():
    setup_config = {"Data required":False,
                    "Args":["Database","Email"]}
    return setup_config

def run(*args):
    db = args[0][0]
    email = args[0][1]
    st.header('Maps')
    st.markdown('####')
    maps_data = db.collection('Users').document(email).collection('PLUGINS').document('Maps').get().to_dict()
    if 'Map_data' not in st.session_state:
        st.session_state['Map_data']=maps_data
    Name_in,Location_in,section_in,=st.columns([2,2,2])
    st.write('---')
    dvid = st.columns([1,1,1])
    name=Name_in.text_input('Name',key='mp_nam')
    if name=='':
        off=True
    else:
        off=False
    def click_button_loc():
        if off==False:
            st.session_state['Map_data'][name]={'Location':st.session_state.mp_loc_,'Section':{}}
            st.session_state.mp_nam=''
            st.session_state.mp_loc_=''
    Location_in.text_input('Location',key='mp_loc_',disabled=off, on_change=click_button_loc)
    kys1=list(st.session_state['Map_data'].keys())
    if len(kys1)!=0:
        rad1 = dvid[0].radio('Location',kys1,key='rad1_loc')        
        def del_Location():
            del st.session_state['Map_data'][rad1]
        def rename_Location():
            if rad1!=st.session_state['Location_u'+rad1]:
                st.session_state['Map_data'][st.session_state['Location_u'+rad1]]=st.session_state['Map_data'].pop(rad1)
        def rename_Location_a():
            if rad1!=st.session_state['Location_u_a'+rad1]:
                st.session_state['Map_data'][rad1]['Location']=st.session_state['Location_u_a'+rad1]
        dvid[0].text_input('Rename',key='Location_u'+rad1,value=rad1, on_change=rename_Location)
        dvid[0].text_input('Edit location',key='Location_u_a'+rad1,value=st.session_state['Map_data'][rad1]['Location'], on_change=rename_Location_a)
        dvid[0].button('Delete',key='Location'+rad1,on_click = del_Location)  
        def click_button_sec():
            if st.session_state.mp_sec!='':
                st.session_state['Map_data'][rad1]['Section'][st.session_state.mp_sec]=''
                st.session_state.mp_sec=''
        section_in.text_input('Section',key='mp_sec', on_change=click_button_sec)
        kys2=list(st.session_state['Map_data'][rad1]['Section'].keys())
        if len(kys2)!=0: 
            rad2=dvid[1].radio('Section',kys2,key='rad2_loc')
            def del_section():
                del st.session_state['Map_data'][rad1]['Section'][rad2]
            def rename_section():
                if rad2!=st.session_state['Section_u'+rad2]:
                    st.session_state['Map_data'][rad1]['Section'][st.session_state['Section_u'+rad2]]=st.session_state['Map_data'][rad1]['Section'].pop(rad2)
            dvid[1].text_input('Rename',key='Section_u'+rad2,value=rad2, on_change=rename_section)
            dvid[1].button('Delete',key='Section'+rad2,on_click = del_section)
            def update_Section_val():
                st.session_state['Map_data'][rad1]['Section'][rad2]=st.session_state[rad1+rad2]
            dvid[2].text_area(rad2,on_change=update_Section_val ,key=rad1+rad2,value=st.session_state['Map_data'][rad1]['Section'][rad2])
    st.write('---')
    if len(kys1)!=0:
        if len(st.session_state['Map_data'][rad1]['Location'].split(' '))==4:
            x_co = float(st.session_state['Map_data'][rad1]['Location'].split(' ')[1])
            y_co = float(st.session_state['Map_data'][rad1]['Location'].split(' ')[-1])
        elif len(st.session_state['Map_data'][rad1]['Location'].split(' '))==2:
            x_co = float(st.session_state['Map_data'][rad1]['Location'].split(' ')[0][:-1])
            y_co = float(st.session_state['Map_data'][rad1]['Location'].split(' ')[1])
        map_draw = folium.Map(location=[x_co, y_co], zoom_start=13)
    else: 
        map_draw = folium.Map(location=[31.535769249543304, 76.89800904547637], zoom_start=13)
    map_draw.add_child(folium.LatLngPopup())
    for i in st.session_state['Map_data']:
        strin = ''
        for j in st.session_state['Map_data'][i]['Section']:
            strin += f"<h2> {j} </h2><ul>"
            for k in (st.session_state['Map_data'][i]['Section'][j].split('\n')):
                strin += f"<li>{k}</li>"
            strin +=  '</ul>'
        html = f"""
                <h1> {i}</h1>
                {strin}
                """
        iframe = branca.element.IFrame(html=html, width=300, height=200)
        popup = folium.Popup(iframe, max_width=300)
        if len(st.session_state['Map_data'][i]['Location'].split(' '))==4:
            x_co = float(st.session_state['Map_data'][i]['Location'].split(' ')[1])
            y_co = float(st.session_state['Map_data'][i]['Location'].split(' ')[-1])
        elif len(st.session_state['Map_data'][i]['Location'].split(' '))==2:
            x_co = float(st.session_state['Map_data'][i]['Location'].split(' ')[0][:-1])
            y_co = float(st.session_state['Map_data'][i]['Location'].split(' ')[1])
        folium.Marker([x_co, y_co]
                        , popup=popup, tooltip=i).add_to(map_draw)
    folium_static(map_draw, width=937, height=550)
    if dvid[2].button('Export'):
        map_draw = folium.Map(location=[31.1611, 76.9180], zoom_start=8, width=383, height=725)
        for i in st.session_state['Map_data']:
            strin = ''
            for j in st.session_state['Map_data'][i]['Section']:
                strin += f"<h2> {j} </h2><ul>"
                for k in (st.session_state['Map_data'][i]['Section'][j].split('\n')):
                    strin += f"<li>{k}</li>"
                strin +=  '</ul>'
            html = f"""
                    <h1> {i}</h1>
                    {strin}
                    """
            iframe = branca.element.IFrame(html=html, width=250, height=200)
            popup = folium.Popup(iframe, max_width=300)
            if len(st.session_state['Map_data'][i]['Location'].split(' '))==4:
                x_co = float(st.session_state['Map_data'][i]['Location'].split(' ')[1])
                y_co = float(st.session_state['Map_data'][i]['Location'].split(' ')[-1])
            elif len(st.session_state['Map_data'][i]['Location'].split(' '))==2:
                x_co = float(st.session_state['Map_data'][i]['Location'].split(' ')[0][:-1])
                y_co = float(st.session_state['Map_data'][i]['Location'].split(' ')[1])
            folium.Marker([x_co, y_co], popup=popup, tooltip=i).add_to(map_draw)
        draw = folium.plugins.Draw(export=True)
        draw.add_to(map_draw)
        fig = Figure(width=383, height=725)
        fig.add_child(map_draw)
        fig.save('/'.join(os.getcwd().split('/')[:-1])+'/map2.html')  
    db.collection('Users').document(email).collection('PLUGINS').document('Maps').set(st.session_state['Map_data'])

def make_templete(db,email):
    template={}
    plugin_list = db.collection('Users').document(email).collection('PLUGINS').get()
    plugin_list = [i.id for i in plugin_list]
    if 'Maps' not in plugin_list:
        db.collection('Users').document(email).collection('PLUGINS').document('Maps').set(template)
    return