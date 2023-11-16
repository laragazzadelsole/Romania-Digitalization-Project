import streamlit as st
import json
from fixed_components import *
from changing_components import *
import numpy as np

st.set_page_config(layout="wide")

initialize_session_state()

# Read the JSON file
config_file = open('config.json')
config = json.load(config_file)


header_config = config['header']
survey_title_subtitle(header_config)

consent_form()

if st.session_state['consent']:

    personal_information()
    instructions()

    q1_config = config['question1']
    updated_bins_question_1_df, percentage_difference1, num_bins1 = create_question(q1_config)

    q2_config = config['question2']
    updated_bins_question_2_df, percentage_difference2, num_bins2 = create_question(q2_config)
    
    
    q3_config = config['question3']
    updated_bins_question_3_df, percentage_difference3, num_bins3 = create_question(q3_config)

    q4_config = config['question4']
    updated_bins_question_4_df, percentage_difference4, num_bins4 = create_question(q4_config)

    q5_config = config['question5']
    updated_bins_question_5_df, percentage_difference5, num_bins5 = create_question(q5_config)

    q6_config = config['question6']
    updated_bins_question_6_df, percentage_difference6, num_bins6 = create_question(q6_config)

    q7_config = config['question7']
    updated_bins_question_7_df, percentage_difference7, num_bins7 = create_question(q7_config) 
    
    q8_config = config['question8']
    updated_bins_question_8_df, percentage_difference8, num_bins8 = create_question(q8_config)

    q9_config = config['question9']
    updated_bins_question_9_df, percentage_difference9, num_bins9 = create_question(q9_config)

    q10_config = config['question10']
    updated_bins_question_10_df, percentage_difference10, num_bins10 = create_question(q10_config)

    
    percentage_differences = [percentage_difference1, percentage_difference2] #, percentage_difference3, percentage_difference4, percentage_difference5, percentage_difference6, percentage_difference7, percentage_difference8, percentage_difference9, percentage_difference10, percentage_difference11]

    updated_bins_list = [updated_bins_question_1_df, updated_bins_question_2_df]#, updated_bins_question_3_df, updated_bins_question_4_df, updated_bins_question_5_df, updated_bins_question_6_df, updated_bins_question_7_df, updated_bins_question_8_df, updated_bins_question_9_df, updated_bins_question_10_df, updated_bins_question_11_df]
    # Submission button + saving data 
    if all(percentage == 0 for percentage in percentage_differences):
        submit = st.button("Submit", on_click = add_submission, args = (updated_bins_question_1_df, updated_bins_question_2_df, updated_bins_question_3_df, updated_bins_question_4_df, updated_bins_question_5_df, updated_bins_question_6_df, updated_bins_question_7_df, updated_bins_question_8_df, updated_bins_question_9_df, updated_bins_question_10_df))

    if st.session_state['submit']:
        
        st.success(f"Thank you for completing the {header_config['survey_title']}!")