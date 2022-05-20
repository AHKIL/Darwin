import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

#-------------------------------------------------Arithmetic---------------------------------------------------------
def interface():
    setup_config = {"Data required":True,
                    "Args":["Database","Email"]}
    return setup_config
  
def run(*args):
    db = args[0][0]
    email = args[0][1]
    st.header('Notes')
    st.markdown('####')
    def save():
        db.collection('Users').document(email).collection('PLUGINS').document('Notes').set({'Notes': Menu_items_})
    note_menu, note = st.columns([1,2])
    Menu_items_ = db.collection('Users').document(email).collection('PLUGINS').document('Notes').get().to_dict()['Notes']
    if len(Menu_items_)<=0:
        Menu_items_.append('Title\n'+'-'*110+'\n\n')

    Menu_icons_ = ['check-circle']*len(Menu_items_)
    Menu_disp = [ i.split('\n')[0] for i in Menu_items_]
    with note_menu.container():
        nav_bar = option_menu("All Notes",Menu_disp, icons=Menu_icons_, menu_icon="journal",
                                styles={
                                "nav": {'overflow-y': "auto","display":"inline-block","height": "220px"},
                                "container": {"background-color":"#0d1017"}
                            })
    def updt_note():
        Menu_items_[Menu_disp.index(nav_bar)] = st.session_state.ac_note
        save()
    note.text_area('Note',Menu_items_[Menu_disp.index(nav_bar)],height=270,on_change = updt_note, key='ac_note')
    creat,delete,emp = st.columns([2,2,8.5])
    def add_note():
        Menu_items_.insert(0,'Title\n'+'-'*110+'\n\n')
        save()
    def del_note():
        st.session_state['on_title']=0
        Menu_items_.pop(Menu_disp.index(nav_bar))
        save()
    creat.button('Create New Note',on_click=add_note)
    delete.button('Delete Note',on_click=del_note)
    st.write('')
    
def make_templete(db,email):
    template = {'Notes':[]}
    plugin_list = db.collection('Users').document(email).collection('PLUGINS').get()
    plugin_list = [i.id for i in plugin_list]
    if 'Notes' not in plugin_list:
        db.collection('Users').document(email).collection('PLUGINS').document('Notes').set(template)