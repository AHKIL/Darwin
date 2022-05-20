import streamlit as st
import datetime
import datefinder
from SERVICES.Create_Service import Create_Service

#-------------------------------------------------Calendar---------------------------------------------------------
def interface():
    setup_config = {"Data required":False,
                    "Args":["Status","Database","Email"]}
    return setup_config

def run(*args):
    status = args[0][0]
    db = args[0][1]
    email = args[0][2]
    if status == ':seedling:'+' Online':
        st.header('Calendar')
        st.markdown('####')
        ev=st.columns([10,2])
        ev[-1].write('Upcoming Events') 
        st.markdown('####') 
        API_NAME = "calendar"
        API_VERSION = "v3"
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        global service
        service =  Create_Service(db, email, API_NAME, API_VERSION, SCOPES)
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                            maxResults=8, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])
        events_col=st.columns(4)
        rem=st.columns([8,1])
        rem[-1].write('Reminders')
        st.markdown('####') 
        reminder_col=st.columns(4)
        not_reminders=[]
        reminders=[]
        i=0
        while len(not_reminders)!=4:
            if 'description' in list(events[i].keys()) and events[i]['description'] == 'Reminder':
                reminders.append(events[i])
            else:
                not_reminders.append(events[i])
            i+=1
        for i,j,event in zip(events_col,range(len(not_reminders)),not_reminders):
            with i:
                with i.form(str(j)):
                    starte = event['start'].get('dateTime', event['start'].get('date'))
                    ende = event['end'].get('dateTime', event['end'].get('date'))
                    matches = list(datefinder.find_dates(starte))
                    endmatches = list(datefinder.find_dates(ende))
                    c = endmatches[0]-matches[0]
                    if len(event['summary'])>28:
                        st.subheader(event['summary'][:25]+"...")
                    else:
                        st.subheader(event['summary'])
                    if datetime.datetime.now().strftime("%b %d %Y")==matches[0].strftime("%b %d %Y"):
                        st.write('Today')
                    else:
                        st.write('Tommorow')
                    st.write(matches[0].strftime("%I:%M %p"))
                    st.form_submit_button(f'{c}')
        for i,j,remd in zip(reminder_col,range(len(reminders)),reminders):
            with i:
                with st.form(str(10+j)):
                    startr = remd['start'].get('dateTime', remd['start'].get('date'))
                    matches = list(datefinder.find_dates(startr))
                    if len(remd['summary'])>15:
                        st.subheader(remd['summary'][:12]+"...")
                    else:
                        st.subheader(remd['summary'])
                    if datetime.datetime.now().strftime("%b %d %Y")==matches[0].strftime("%b %d %Y"):
                        st.write('Today')
                    else:
                        st.write('Tommorow')
                    st.write(matches[0].strftime("%I:%M %p"))
                    st.form_submit_button('Mark as done')

    