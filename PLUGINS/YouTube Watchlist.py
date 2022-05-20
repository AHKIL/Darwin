import streamlit as st
from firebase_admin import firestore
import json
from SERVICES.Create_Service import Create_Service

#-------------------------------------------------YouTube Watchlist---------------------------------------------------------
def interface():
    setup_config = {"Data required":True,
                    "Args":["Status","Database","Email"]}
    return setup_config

def run(*args):
    status = args[0][0]
    db = args[0][1]
    email = args[0][2]
    playlist_data = db.collection('Users').document(email).collection('PLUGINS').document('YoutubeWatchlist').get().to_dict()
    st.header('YouTube Watchlist')
    st.markdown('####')
    inp_arr = st.columns(2)
    name=inp_arr[0].text_input('Playlist Name',key='Playlist_Name')
    if name=='':
        off=True
    else:
        off=False
    def click_button_menu():
        if st.session_state.Playlist_ID !='' or st.session_state.Playlist_Name !='':
            youtube_ref = db.collection('Users').document(email).collection('PLUGINS').document('YoutubeWatchlist')
            youtube_ref.update({'plylist': firestore.ArrayUnion([st.session_state.Playlist_ID])})
            youtube_ref.update({'plylist_name': firestore.ArrayUnion([st.session_state.Playlist_Name])})
            st.session_state.Playlist_Name=''
            st.session_state.Playlist_ID=''
    inp_arr[1].text_input('Playlist ID',key='Playlist_ID',disabled=off, on_change=click_button_menu)

    def youtube_link_extractor(playlistId_Source):
        API_NAME  =  'youtube'
        API_VERSION  =  'v3'
        SCOPES  = ['https://www.googleapis.com/auth/youtube']
        global service
        service =  Create_Service(db, email, API_NAME, API_VERSION, SCOPES)
        response = service.playlistItems().list(
            part='contentDetails',
            playlistId=playlistId_Source,
            maxResults=50
        ).execute()

        playlistItems = response['items']
        nextPageToken = response.get('nextPageToken')
        while nextPageToken:
            response = service.playlistItems().list(
                part='contentDetails',
                playlistId=playlistId_Source,
                maxResults=50,
                pageToken=nextPageToken
            ).execute()

            playlistItems.extend(response['items'])
            nextPageToken = response.get('nextPageToken')
        return playlistItems

    if status==':seedling:'+' Online' and len(playlist_data['plylist_name'])>0:
        slct_box, ren_ply, del_ply = st.columns([5,5,.9])
        prev_ind = playlist_data['status']
        id_play = slct_box.selectbox('Select Playlist',playlist_data['plylist_name'],index=prev_ind)
        youtube_ref = db.collection('Users').document(email).collection('PLUGINS').document('YoutubeWatchlist')
        youtube_ref.update({'status': playlist_data['plylist_name'].index(id_play)})
        def delete_play():
            del_index = playlist_data['plylist_name'].index(id_play)
            youtube_ref.update({'plylist_name': firestore.ArrayRemove([playlist_data['plylist_name'][del_index]])})
            youtube_ref.update({'plylist': firestore.ArrayRemove([playlist_data['plylist'][del_index]])})
        def rename_playlist():
            playlist_data['plylist_name'][playlist_data['plylist_name'].index(id_play)]=st.session_state['ren_play_'+id_play]
            youtube_ref.set(playlist_data)

        ren_ply.text_input('Rename',on_change=rename_playlist,key='ren_play_'+id_play, value=id_play)
        del_ply.title('')
        del_ply.button('Delete', on_click=delete_play, key='del_playlist'+id_play)
        playlistItems = youtube_link_extractor(playlist_data['plylist'][playlist_data['plylist_name'].index(id_play)])
        size=int(len(playlistItems)/3)
        for i in range(size):
            arr=st.columns([1]*3)
            arr[0].video('https://www.youtube.com/watch?v='+playlistItems[(i*3)]['contentDetails']['videoId'])
            arr[1].video('https://www.youtube.com/watch?v='+playlistItems[(i*3)+1]['contentDetails']['videoId'])
            arr[2].video('https://www.youtube.com/watch?v='+playlistItems[(i*3)+2]['contentDetails']['videoId'])
        arr=st.columns([1]*3)
        for i in range(len(playlistItems)%3):
            arr[i].video('https://www.youtube.com/watch?v='+playlistItems[(size*3)+i]['contentDetails']['videoId']) 

def make_templete(db,email):
    template={'plylist':[],'plylist_name':[],'status':0}
    plugin_list = db.collection('Users').document(email).collection('PLUGINS').get()
    plugin_list = [i.id for i in plugin_list]
    if 'YoutubeWatchlist' not in plugin_list:
        db.collection('Users').document(email).collection('PLUGINS').document('YoutubeWatchlist').set(template)
    return

