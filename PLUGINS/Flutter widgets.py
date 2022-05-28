import streamlit as st

#-------------------------------------------------MAPS---------------------------------------------------------
def interface():
    setup_config = {"Data required":True,
                    "Args":["Database","Email"]}
    return setup_config

def run(*args):
    db = args[0][0]
    email = args[0][1]
    st.header('Flutter Widgets Cheetsheet')
    st.markdown('####')
    Widgets_data = db.collection('Users').document(email).collection('PLUGINS').document('Widgets').get().to_dict()
    if 'Widgets_data' not in st.session_state:
        st.session_state['Widgets_data']=Widgets_data
    language_in,Location_in,WidgetName_in,=st.columns([2,2,2])
    st.write('---')
    dvid = st.columns([1,1,1])
    def click_button_loc():
        if st.session_state['Widgets_data'] == None:
            st.session_state['Widgets_data']={}
        st.session_state['Widgets_data'][st.session_state.language_inp]={'WidgetName':{}}
        save()
        st.session_state.language_inp=''
    language_in.text_input('Category',key='language_inp', on_change=click_button_loc)
    
    def save():
        db.collection('Users').document(email).collection('PLUGINS').document('Widgets').set(st.session_state['Widgets_data'])
    
    if st.session_state['Widgets_data'] == None:
        kys1=[]
    else:
        kys1=list(st.session_state['Widgets_data'].keys())
    if len(kys1)!=0:
        rad1 = dvid[0].radio('Category',kys1,key='language_radio')        
        def del_Location():
            del st.session_state['Widgets_data'][rad1]
            save()
        def rename_Location():
            if rad1!=st.session_state['language_rename'+rad1]:
                st.session_state['Widgets_data'][st.session_state['language_rename'+rad1]]=st.session_state['Widgets_data'].pop(rad1)
                save()
        dvid[0].text_input('Rename',key='language_rename'+rad1,value=rad1, on_change=rename_Location)
        dvid[0].button('Delete',key='Language'+rad1,on_click = del_Location)  
        def click_button_sec():
            if st.session_state.widget_name!='':
                st.session_state['Widgets_data'][rad1]['WidgetName'][st.session_state.widget_name]=''
                save()
                st.session_state.widget_name=''
        WidgetName_in.text_input('Widget Name',key='widget_name', on_change=click_button_sec)
        kys2=list(st.session_state['Widgets_data'][rad1]['WidgetName'].keys())
        if len(kys2)!=0: 
            rad2=dvid[1].radio('Widget Name',kys2,key='rad2_loc') 
            def del_WidgetName():
                del st.session_state['Widgets_data'][rad1]['WidgetName'][rad2]
                save()
            def rename_WidgetName():
                if rad2!=st.session_state['WidgetName_u'+rad2]:
                    st.session_state['Widgets_data'][rad1]['WidgetName'][st.session_state['WidgetName_u'+rad2]]=st.session_state['Widgets_data'][rad1]['WidgetName'].pop(rad2)
                    save()
            dvid[1].text_input('Rename',key='WidgetName_u'+rad2,value=rad2, on_change=rename_WidgetName)
            dvid[1].button('Delete',key='WidgetName'+rad2,on_click = del_WidgetName)
            def update_WidgetName_val():
                st.session_state['Widgets_data'][rad1]['WidgetName'][rad2]=st.session_state[rad1+rad2]
                save()
            dvid[2].text_area(rad2,on_change=update_WidgetName_val , height = 232,
                              key=rad1+rad2,value=st.session_state['Widgets_data'][rad1]['WidgetName'][rad2])
    st.write('---')
    st.subheader('Code Snippet')
    st.code(st.session_state['Widgets_data'][rad1]['WidgetName'][rad2])

def make_templete(db,email):
    template={}
    plugin_list = db.collection('Users').document(email).collection('PLUGINS').get()
    plugin_list = [i.id for i in plugin_list]
    if 'Widgets' not in plugin_list:
        db.collection('Users').document(email).collection('PLUGINS').document('Widgets').set(template)
    return
