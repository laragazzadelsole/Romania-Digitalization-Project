            
import streamlit as st
import streamlit.components.v1 as components
import numpy as np
#from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode
import io
import numpy as np
from google.oauth2 import service_account
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from requests_oauthlib import OAuth2Session
import csv
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from fixed_components import *
import sympy as sy

def initialize_session_state():
    if 'key' not in st.session_state:
        st.session_state['key'] = 'value'
        st.session_state['consent'] = False
        st.session_state['submit'] = False
        st.session_state['No answer'] = ''
       
    if 'data' not in st.session_state:
        st.session_state['data'] = {
            'User Full Name': [],
            'User Working Position': [],
            'User Professional Category': [],
            'Minimum Effect Size Q1': [],
            'Minimum Effect Size Q2': [],    
            'Minimum Effect Size Q3': [],
            'Minimum Effect Size Q4': [],
   
            'Minimum Effect Size Q5': [],
    
            'Minimum Effect Size Q6': [],
    
            'Minimum Effect Size Q7': [],

            'Minimum Effect Size Q8': [],

            'Minimum Effect Size Q9': [],
   
            'Minimum Effect Size Q10': []

            }

def safe_var(key):
    if key in st.session_state:
        return st.session_state[key]
    #return st.session_state['No answer']

def survey_title_subtitle(header_config):
    st.title(header_config['survey_title'])
    st.write(header_config['survey_description'])
    st.write(st.__version__)

@st.cache_data(persist=True)
def create_question(jsonfile_name):
    minor_value = str(jsonfile_name['minor_value'])
    min_value = float(jsonfile_name['min_value_graph'])
    max_value = float(jsonfile_name['max_value_graph'])
    interval = float(jsonfile_name['step_size_graph'])
    major_value = jsonfile_name['major_value']

    # Create a list of ranges based on the provided values
    x_axis = [f"{i}-{(i+interval)}" for i in range(int(min_value), int(max_value), int(interval))]
    # Add minor_value at the beginning
    x_axis.insert(0, minor_value)

    # Add major_value at the end
    x_axis.append(major_value)

    y_axis = np.zeros(len(x_axis))
    data = pd.DataFrame(list(zip(x_axis, y_axis)), columns=[jsonfile_name['column_1'], jsonfile_name['column_2']])

    data_container = st.container()
    placeholder = st.empty()
    with placeholder.container():
        with st.expander(jsonfile_name['question_number'], expanded=True):

            st.subheader(jsonfile_name['title_question'])
            st.write(jsonfile_name['subtitle_question'])
            data_container = st.container()
            with data_container:
                table, plot = st.columns([0.4, 0.6], gap="large")
                with table:
                    bins_grid = st.data_editor(data, key= jsonfile_name['key'], use_container_width=True, hide_index=True, disabled=[jsonfile_name['column_1']])
                    
                    # Initialize the counter
                    total_percentage = int(100)
                    # Calculate the new total sum
                    percentage_inserted= sum(bins_grid[jsonfile_name['column_2']])
                    # Calculate the difference in sum
                    percentage_difference = total_percentage - percentage_inserted
                    # Update the counter
                    total_percentage = percentage_difference

                    # Display the counter
                    if percentage_difference >= 0:
                        st.write(f"**You still have to allocate {percentage_difference} percent probability.**")
                    else:
                        st.write(f'**:red[You have inserted {abs(percentage_difference)} percent more, please review your percentage distribution.]**')

                    num_bins = len(bins_grid)
                
                with plot:
                    st.bar_chart(bins_grid, x = jsonfile_name['column_1'], y = jsonfile_name['column_2'])
                
            #st.write(jsonfile_name['effect_size'])
            #st.number_input('Click to increase and decrease the counter or directly insert the number.', min_value=0, max_value=10000, key = jsonfile_name['num_input_question'])

            # Return the updated DataFrame
            updated_bins_df = pd.DataFrame(bins_grid)
            return updated_bins_df, percentage_difference, num_bins
        
def min_effect_size_question(jsonfile_name):
    st.write(jsonfile_name['effect_size'])
    st.number_input('Click to increase and decrease the counter or directly insert the number.', min_value=0, max_value=10000, key = jsonfile_name['num_input_question'])


def add_submission(updated_bins_question_1_df, updated_bins_question_2_df, updated_bins_question_3_df, updated_bins_question_4_df, updated_bins_question_5_df, updated_bins_question_6_df, updated_bins_question_7_df, updated_bins_question_8_df, updated_bins_question_9_df, updated_bins_question_10_df):
    st.session_state['submit'] = True

    updated_bins_list = [updated_bins_question_1_df, updated_bins_question_2_df, updated_bins_question_3_df, updated_bins_question_4_df, updated_bins_question_5_df, updated_bins_question_6_df, updated_bins_question_7_df, updated_bins_question_8_df, updated_bins_question_9_df, updated_bins_question_10_df]
    transposed_bins_list = []

    for df in updated_bins_list:
        transposed_df = df.transpose()
        transposed_bins_list.append(transposed_df)
    
    
    # Extracting the first row of each transposed dataframe as column names
    column_names_q1 = list(transposed_bins_list[0].iloc[0])
    column_names_q2 = list(transposed_bins_list[1].iloc[0])
    column_names_q3 = list(transposed_bins_list[2].iloc[0])
    column_names_q4 = list(transposed_bins_list[3].iloc[0])
    column_names_q5 = list(transposed_bins_list[4].iloc[0])
    column_names_q6 = list(transposed_bins_list[5].iloc[0])
    column_names_q7 = list(transposed_bins_list[6].iloc[0])
    column_names_q8 = list(transposed_bins_list[7].iloc[0])
    column_names_q9 = list(transposed_bins_list[8].iloc[0])
    column_names_q10 = list(transposed_bins_list[9].iloc[0])

    # Setting the column names for each dataframe
    transposed_bins_list[0].columns = column_names_q1
    transposed_bins_list[1].columns = column_names_q2
    transposed_bins_list[2].columns = column_names_q3
    transposed_bins_list[3].columns = column_names_q4
    transposed_bins_list[4].columns = column_names_q5
    transposed_bins_list[5].columns = column_names_q6
    transposed_bins_list[6].columns = column_names_q7
    transposed_bins_list[7].columns = column_names_q8
    transposed_bins_list[8].columns = column_names_q9
    transposed_bins_list[9].columns = column_names_q10

    # Removing the first row (used as column names) from each dataframe
    transposed_bins_list[0] = transposed_bins_list[0].iloc[1:]
    transposed_bins_list[1] = transposed_bins_list[1].iloc[1:]
    transposed_bins_list[2] = transposed_bins_list[2].iloc[1:]
    transposed_bins_list[3] = transposed_bins_list[3].iloc[1:]
    transposed_bins_list[4] = transposed_bins_list[4].iloc[1:]
    transposed_bins_list[5] = transposed_bins_list[5].iloc[1:]
    transposed_bins_list[6] = transposed_bins_list[6].iloc[1:]
    transposed_bins_list[7] = transposed_bins_list[7].iloc[1:]
    transposed_bins_list[8] = transposed_bins_list[8].iloc[1:]
    transposed_bins_list[9] = transposed_bins_list[9].iloc[1:]

    # Adding 'Q1' prefix to column names of the first dataframe in the list
    transposed_bins_list[0].columns = ['Q1  ' + str(col) for col in transposed_bins_list[0].columns]
    transposed_bins_list[1].columns = ['Q2  ' + str(col) for col in transposed_bins_list[1].columns]
    transposed_bins_list[2].columns = ['Q3  ' + str(col) for col in transposed_bins_list[2].columns]
    transposed_bins_list[3].columns = ['Q4  ' + str(col) for col in transposed_bins_list[3].columns]
    transposed_bins_list[4].columns = ['Q5  ' + str(col) for col in transposed_bins_list[4].columns]
    transposed_bins_list[5].columns = ['Q6  ' + str(col) for col in transposed_bins_list[5].columns]
    transposed_bins_list[6].columns = ['Q7  ' + str(col) for col in transposed_bins_list[6].columns]
    transposed_bins_list[7].columns = ['Q8  ' + str(col) for col in transposed_bins_list[7].columns]
    transposed_bins_list[8].columns = ['Q9  ' + str(col) for col in transposed_bins_list[8].columns]
    transposed_bins_list[9].columns = ['Q10  ' + str(col) for col in transposed_bins_list[9].columns]

    df1 = transposed_bins_list[0]
    df2 = transposed_bins_list[1]
    df3 = transposed_bins_list[2]
    df4 = transposed_bins_list[3]
    df5 = transposed_bins_list[4]
    df6 = transposed_bins_list[5]
    df7 = transposed_bins_list[6]
    df8 = transposed_bins_list[7]
    df9 = transposed_bins_list[8]
    df10 = transposed_bins_list[9]


    questions_df = pd.concat([df1,df2.set_index(df1.index), df3.set_index(df1.index), df4.set_index(df1.index), df5.set_index(df1.index), df6.set_index(df1.index), df7.set_index(df1.index), df8.set_index(df1.index), df9.set_index(df1.index), df10.set_index(df1.index)], axis=1)


    # Resetting index if needed
    questions_df.reset_index(drop=True, inplace=True)
    
     
    # Update session state
    data = st.session_state['data']

    USER_FULL_NAME = 'User Full Name'
    USER_PROF_CATEGORY = 'User Professional Category'
    USER_POSITION = 'User Working Position'
    MIN_EFF_SIZE_Q1 = 'Minimum Effect Size Q1'
    MIN_EFF_SIZE_Q2 = 'Minimum Effect Size Q2'
    MIN_EFF_SIZE_Q3 = 'Minimum Effect Size Q3'
    MIN_EFF_SIZE_Q4 = 'Minimum Effect Size Q4'
    MIN_EFF_SIZE_Q5 = 'Minimum Effect Size Q5'
    MIN_EFF_SIZE_Q6 = 'Minimum Effect Size Q6'
    MIN_EFF_SIZE_Q7 = 'Minimum Effect Size Q7'
    MIN_EFF_SIZE_Q8 = 'Minimum Effect Size Q8'
    MIN_EFF_SIZE_Q9 = 'Minimum Effect Size Q9'
    MIN_EFF_SIZE_Q10 = 'Minimum Effect Size Q10'


    data[USER_FULL_NAME].append(safe_var('user_full_name'))
    data[USER_POSITION].append(safe_var('user_position'))
    data[USER_PROF_CATEGORY].append(safe_var('professional_category'))
    data[MIN_EFF_SIZE_Q1].append(safe_var('num_input_question1'))
    data[MIN_EFF_SIZE_Q2].append(safe_var('num_input_question2'))
    data[MIN_EFF_SIZE_Q3].append(safe_var('num_input_question3'))
    data[MIN_EFF_SIZE_Q4].append(safe_var('num_input_question4'))
    data[MIN_EFF_SIZE_Q5].append(safe_var('num_input_question5'))
    data[MIN_EFF_SIZE_Q6].append(safe_var('num_input_question6'))
    data[MIN_EFF_SIZE_Q7].append(safe_var('num_input_question7'))
    data[MIN_EFF_SIZE_Q8].append(safe_var('num_input_question8'))
    data[MIN_EFF_SIZE_Q9].append(safe_var('num_input_question9'))
    data[MIN_EFF_SIZE_Q10].append(safe_var('num_input_question10'))                                    
  

    st.session_state['data'] = data
    
    session_state_df = pd.DataFrame(data)
    personal_data_df = session_state_df.iloc[:, :3]
    min_eff_df = session_state_df.iloc[:, 3:]

 
    concatenated_df = pd.concat([personal_data_df, questions_df.set_index(personal_data_df.index), min_eff_df.set_index(personal_data_df.index)], axis=1)

   
    #save data to google sheet --> CREATE NEW API CONNECTION FOR THE PROJECT
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    

    #creds = ServiceAccountCredentials.from_json_keyfile_name('prior-beliefs-elicitation-keys.json', scope)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(secrets_to_json(), scope)
    client = gspread.authorize(creds)

    # Load the Google Sheet romania-project@romania-digitalization-project.iam.gserviceaccount.com
    sheet = client.open("WB project").sheet1
    #spreadsheet_id = "1AXMfEidiJp_-ykkgt1t_vIO1lFcNTZ_5u3-m72a5gEA/edit#gid=0"
    #sheet_name = "Sheet1"
    #sheet = client.open("WB project").sheet1
    column_names_list = concatenated_df.columns.tolist()
    #test_sheet = client.create(f'Test for Romania').sheet1
   # sheet_col_update = sheet.append_row([concatenated_df.columns.values.tolist()])
    column_names = sheet.append_row(column_names_list)
    sheet_row_update = sheet.append_rows(concatenated_df.values.tolist()) #.values.tolist())
    #duplicate = sheet.duplicate(new_sheet_name='Duplicate data')
    #st.success('Data has been saved successfully.')
    
    #Navigate to the folder in Google Drive. Copy the Folder ID found in the URL. This is everything that comes after “folder/” in the URL.
   # backup_sheet = client.create(f'Backup_{datetime.now()}', folder_id='1stjn5pLHr3rZ89n6QndKSBJoKBLtuK-u').sheet1
    #backup_sheet = backup_sheet.append_rows(concatenated_df.values.tolist()) #(new_bins_df.iloc[:2].values.tolist())
    #backup_sheet.share('sara.gironi97@gmail.com', perm_type = 'user', role = 'writer')

    