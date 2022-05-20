import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage
import streamlit as st
import pyrebase
import json
import glob
from streamlit_option_menu import option_menu
import importlib
import socket

st.set_page_config(layout="wide",page_title="Darwin")
hide_st_style = """<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>"""

firebase_cred=dict(st.secrets)
firebase_cred.pop('web')

firebaseConfig = {
  'apiKey': "AIzaSyCb38ZtziMFyfmj-X9UhBMZokc3UApV0N0",
  'authDomain': "darwin-58a70.firebaseapp.com",
  'projectId': "darwin-58a70",
  'storageBucket': "darwin-58a70.appspot.com",
  'messagingSenderId': "97039718621",
  'appId': "1:97039718621:web:3d624b77e2eb5e3443a334",
  'measurementId': "G-JV4JQR2BGQ",
  "databaseURL": "",
  "serviceAccount": firebase_cred
}

firebase = pyrebase.initialize_app(firebaseConfig)
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_cred)
    firebase_admin.initialize_app(cred)

db = firestore.client()
Storage = firebase.storage()
bucket = storage.bucket(firebaseConfig['storageBucket'])

if 'auth' not in st.session_state:
    st.session_state['auth'] = firebase.auth()
if 'Login_status' not in st.session_state:
    st.session_state['Login_status'] = 'Sign in'
if 'user_details' not in st.session_state:
    st.session_state['user_details'] = None

def change_to_signup():
    st.session_state['Login_status'] = 'Sign up'

def change_to_signin():
    st.session_state['Login_status'] = 'Sign in'

def signup():
    def user_signup():
        if password!= Con_password:
            st.error('Password does not match')
            return
        if info_['Workspace Name']=='':
            st.error('All fields are required')
            return
        try:
            st.session_state['auth'].create_user_with_email_and_password(st.session_state.email, st.session_state.password)
            st.success('Email created successfully')
            db.collection('Users').document(st.session_state.email).set(info_)
            st.session_state['Login_status'] = 'Sign in'
        except Exception as e:
            st.error(json.loads(e.args[1])['error']['message'].replace('_', ' '))

    si = st.columns([0.5,1,0.6,1,0.4])
    si[1].title('Sign Up')
    si[3].title('')
    si[3].title('')
    si[3].title('Darwin')
    text_signup = st.columns([1,1,1,4])
    text_signup[1].write('Already have an account')
    text_signup[2].button('Sign in', on_click=change_to_signin)
    info_={}
    with si[1].container():
        info_['Workspace Name'] = st.text_input('Workspace Name',key = 'Workspace Name', placeholder = 'Workspace Name')
        st.text_input('Email',key = 'email', placeholder = 'Email')
        password = st.text_input('Password',key = 'password', placeholder = 'Password',type='password')
        Con_password = st.text_input('Confirm Password',key = 'Con_password', placeholder = 'Password',type='password')
        info_['Phone Number'] = st.text_input('Phone Number',key = 'Phone Number', placeholder = '+91')
        info_['Menu'] = {"Settings": {"icon": "gear", "Plugins": []}}
        st.button('Sign up', on_click=user_signup)
            
def signin():
    def user_signin():
        try:
            st.session_state['auth'].sign_in_with_email_and_password(st.session_state.email_signin, st.session_state.password_signin)
            st.session_state['user_details'] = st.session_state['auth'].current_user
        except Exception as e: 
            st.error(json.loads(e.args[1])['error']['message'].replace('_', ' '))
    si = st.columns([0.5,1,0.6,1,0.4])
    si[1].title('Sign in')
    si[3].title('')
    si[3].title('')
    si[3].title('Darwin')
    text_signup = st.columns([1,1,1,4])
    text_signup[1].write('Do not have an account')
    text_signup[2].button('Sign up', on_click=change_to_signup)
    with si[1].container():
        st.text_input('Email',key = 'email_signin', placeholder = 'Email')
        st.text_input('Password',key = 'password_signin', placeholder = 'Password',type='password')
        st.button('Sign in', on_click= user_signin)

if st.session_state['user_details'] == None:
    if st.session_state['Login_status'] == 'Sign in':
        signin()
    if st.session_state['Login_status'] == 'Sign up':
        signup()
    st.stop()

Presets = db.collection('Users').document(st.session_state['user_details']['email']).get().to_dict()
if 'Menu' not in st.session_state:
    st.session_state['Menu']=Presets['Menu']
#---------------------------------------------Menu_edit-----------------------------------------------------
def Menu_edit():
    menu,icon=st.columns(2)
    st.write('---')
    dvid = st.columns([2,3,.5,4])
    name=menu.text_input('Add to Menu',key='admnu')
    if name=='':
        off=True
    else:
        off=False
    def save():
        db.collection('Users').document(st.session_state['user_details']['email']).update({'Menu':st.session_state['Menu']})
    def click_button_menu():
        if off==False:
            st.session_state['Menu'][name]={'icon':st.session_state.icon_,'Plugins':[]}
            st.session_state.admnu=''
            st.session_state.icon_='columns'
            save()
    with open("Assets/icon_list.json", "r") as fp:   
        icon_list = json.load(fp)
    icon.selectbox('Icon',icon_list,key='icon_',disabled=off, on_change=click_button_menu)
    kys1=list(st.session_state['Menu'].keys())
    rad1 = dvid[0].radio('Menu Items',kys1)
    def del_menu():
        del st.session_state['Menu'][rad1]
        save()
    def rename_menu():
        if rad1!=st.session_state['men'+rad1]:
            st.session_state['Menu'][st.session_state['men'+rad1]]=st.session_state['Menu'].pop(rad1)
            save()
        if rad1 == Presets['DefaultMenu']:
            db.collection('Users').document(st.session_state['user_details']['email']).update({'DefaultMenu':st.session_state['men'+rad1]})
    def change_icon():
        st.session_state['Menu'][rad1]['icon']=st.session_state['men_icon'+rad1]
        save()
    if rad1!='Settings':
        dvid[1].text_input('Rename',key='men'+rad1,value=rad1, on_change=rename_menu)
        dvid[1].selectbox('Change icon',
                            icon_list,key='men_icon'+rad1,
                            index=icon_list.index(st.session_state['Menu'][rad1]['icon']), 
                            on_change=change_icon)
        dvid[1].button('Delete',key='menu_del'+rad1,on_click = del_menu)  
    def update_plugins():
        st.session_state['Menu'][rad1]['Plugins']=st.session_state[rad1+'plugins']
        save()
    dvid[3].multiselect('Plugins',
                        [plug.split('/')[-1].split('.')[0] for plug in glob.glob('PLUGINS/*')], 
                        on_change=update_plugins,  
                        key=rad1+'plugins', format_func = lambda x: x.replace('_', ' '),
                        default=st.session_state['Menu'][rad1]['Plugins'])

#---------------------------------------------Settings-----------------------------------------------------
def Settings():
    Title,date,dtext=st.columns([20,1,3])
    Title.title('Settings')
    date.markdown("# :date:")
    dtext.markdown(f"""<h3 style='text-align: right'>{datetime.datetime.now().strftime("%b %d %Y")}</h3>""",True)
    st.title('')
    Menu_edit()
    st.write('---')

#-----------------------------------------------Main-------------------------------------------------------
def main():                                                                                                           
    Menu_items_ = list(st.session_state['Menu'].keys())
    Menu_icons_ = list([st.session_state['Menu'][i]['icon'] for i in Menu_items_])
    REMOTE_SERVER = "one.one.one.one"
    def is_connected(hostname):
        try:
            host = socket.gethostbyname(hostname)
            s = socket.create_connection((host, 80), 2)
            s.close()
            return ':seedling:'+' Online'
        except:
            pass
        return ':exclamation:'+' Offline'
    status=is_connected(REMOTE_SERVER)

    if Presets['MenuStyle'] == 'Left':
        with st.sidebar:
            nav_bar = option_menu('Menu',Menu_items_, icons=Menu_icons_, menu_icon="check2-circle", 
                                  default_index=Menu_items_.index(Presets['DefaultMenu']))
            st.write(status)

    elif Presets['MenuStyle'] == 'Top':
        menu_arr= st.columns([8-len(Menu_items_),1+len(Menu_items_)])
        with menu_arr[1].container():
            nav_bar = option_menu(None,Menu_items_, icons=Menu_icons_, menu_icon="check2-circle", 
                                    default_index=Menu_items_.index(Presets['DefaultMenu']),orientation="horizontal",
                                    styles={"container": {"background-color": "#0d1017", "margin-top": "-10px"}})
        menu_arr[0].write(status)

    if nav_bar=='Settings':
        Settings()
    else:
        Title,date,dtext=st.columns([20,1,3])
        Title.title(nav_bar)
        date.markdown("# :date:")
        dtext.markdown(f"""<h3 style='text-align: right'>{datetime.datetime.now().strftime("%b %d %Y")}</h3>""",True)
    for i in st.session_state['Menu'][nav_bar]['Plugins']:
        st.title('')
        dic = {'Status':status,'Database':db,'Email':st.session_state['user_details']['email'], 'Storage':Storage, 'Bucket':bucket,
                'Menu icons':Menu_icons_,'Menu items':Menu_items_, 'Presets':Presets}
        plug_run = importlib.import_module(f"PLUGINS.{i}")
        setup_config = plug_run.interface()
        if setup_config['Data required']:
            plug_run.make_templete(db, st.session_state['user_details']['email'])
        plug_run.run([dic[pas] for pas in setup_config['Args']])

main()
