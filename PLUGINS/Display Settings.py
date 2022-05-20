import streamlit as st
from streamlit_option_menu import option_menu

#-------------------------------------------------MAPS---------------------------------------------------------
def interface():
    setup_config = {"Data required":False,
                    "Args":["Database","Email",'Menu icons','Menu items','Presets']}
    return setup_config

def run(*args):
    db = args[0][0]
    email = args[0][1]
    Menu_icons_ = args[0][2]
    Menu_items_ = args[0][3]
    Presets = args[0][4]
    st.header('Display')
    st.markdown('####')
    st.subheader('Menu Bar')
    st.markdown('#####')
    menu_bar = st.columns([4,0.5,6])

    with menu_bar[0].container():
        st.write('Left')
        option_menu('Menu',Menu_items_, icons=Menu_icons_, menu_icon="check2-circle", default_index=0,key='lf')
        
    with menu_bar[2].container():
        st.write('Top')
        option_menu(None,Menu_items_, icons=Menu_icons_, menu_icon="check2-circle", default_index=0,orientation="horizontal",
                                    styles={"container": {"background-color": "#0d1017", "margin-top": "-10px"}},key='tp')
    
    def update_menu_style():
        db.collection('Users').document(email).update({'MenuStyle':st.session_state.menu_style})

    def update_default_menu():
        db.collection('Users').document(email).update({'DefaultMenu':st.session_state.default_menu})

    menu_bar_ = st.columns([4,0.5,6])
    with menu_bar_[0].container():
        st.radio('Menu Bar style',['Left','Top'],on_change=update_menu_style, key='menu_style',index=['Left','Top'].index(Presets['MenuStyle']))
        
    with menu_bar_[2].container():
        st.selectbox('Default Menu',Menu_items_, on_change=update_default_menu, key='default_menu', index= Menu_items_.index(Presets['DefaultMenu']))