import streamlit as st
#-------------------------------------------------Bayes Theoram---------------------------------------------------------
def interface():
    setup_config = {"Data required":False,
                    "Args":[]}
    return setup_config

def run(*args):
    st.header('Bayes Theoram')
    st.markdown('####')
    with st.form('Bayes_theoram'):
        prior_belief = st.slider('Prior belief',
                                    min_value=0.01,
                                    max_value=99.99,step=0.01,
                                    value=50.00,
                                    help='What is the previous probability of the hypothesis')
        inp_bayes = st.columns([5,.2,5])
        true_hypothysis = inp_bayes[0].slider('True positives',
                                                min_value=0.00,max_value=100.00,step=0.01,
                                                value=50.00,
                                                help='Probability that the hypothesis is true')
        false_hypothysis = inp_bayes[2].slider('False positives',
                                                min_value=0.00,max_value=100.00,
                                                step=0.01,value=50.00,
                                                help='Probability that not hypothesis is true')
        st.form_submit_button('Calculate')
    updated_belief = (prior_belief*true_hypothysis)/((prior_belief*true_hypothysis)+((100 - prior_belief)*false_hypothysis))
    updated_belief = updated_belief*100
    st.markdown('####')
    st.metric(label="Probability That Hypothysis Is True", 
                value=str(round(updated_belief,2))+" %",
                delta=str(round(updated_belief-prior_belief,2))+" %")