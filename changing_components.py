            
import streamlit as st
import streamlit.components.v1 as components
import numpy as np
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
import altair as alt

def initialize_session_state():
    if 'key' not in st.session_state:
        st.session_state['key'] = 'value'
        st.session_state['consent'] = False
        st.session_state['submit'] = False
        st.session_state['No answer'] = ''
    
    if 'personal_data_df' not in st.session_state:
        st.session_state['personal_data_df'] = pd.DataFrame(columns=['User Full Name', 'User Working Position', 'User Professional Category', 'User Years of Experience'])

    if 'min_eff_df' not in st.session_state:
        st.session_state['min_eff_df'] = pd.DataFrame(columns=['Minimum Effect Size Q1', 'Minimum Effect Size Q2', 'Minimum Effect Size Q3', 'Minimum Effect Size Q6', 'Minimum Effect Size Q7'])
    
    if 'data' not in st.session_state:
        st.session_state['data'] = {
            'User Full Name': [],
            'User Working Position': [],
            'User Professional Category': [],
            'User Years of Experience': [],
            'Minimum Effect Size Q1': [],
            'Minimum Effect Size Q2': [],    
            'Minimum Effect Size Q3': [],
            'Minimum Effect Size Q6': [],
            'Minimum Effect Size Q7': []
            }
    
def safe_var(key):
    if key in st.session_state:
        return st.session_state[key]
    #return st.session_state['No answer']

def survey_title_subtitle(header_config):
    st.title(header_config['survey_title'])
    st.write(header_config['survey_description'])

#@st.cache_data(persist=True)
def create_question(jsonfile_name):

    minor_value = str(jsonfile_name['minor_value'])
    min_value = jsonfile_name['min_value_graph']
    max_value = jsonfile_name['max_value_graph']
    interval = jsonfile_name['step_size_graph']
    major_value = str(jsonfile_name['major_value'])

    # Create a list of ranges based on the provided values

    x_axis = [f"{round(i, 1)}-{round((i + interval), 1)}" for i in np.arange(min_value, max_value, interval)]
    # Add minor_value at the beginning
    x_axis.insert(0, minor_value)

    # Add major_value at the end
    x_axis.append(major_value) 

    y_axis = np.zeros(len(x_axis))
    data = pd.DataFrame(list(zip(x_axis, y_axis)), columns=[jsonfile_name['column_1'], jsonfile_name['column_2']])

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
            if percentage_difference > 0:
                st.write(f"**You still have to allocate {percentage_difference} percent probability.**")
            elif percentage_difference == 0:
                st.write(f'**You have allocated all probabilities!**')
            else:
                st.write(f'**:red[You have inserted {abs(percentage_difference)} percent more, please review your percentage distribution.]**')           
                  
        with plot:
            # Create bar chart with Altair
            chart = alt.Chart(bins_grid).mark_bar().encode(
                x=alt.X(jsonfile_name['column_1'], sort=None),
                y=jsonfile_name['column_2']
            )

            # Display the chart using st.altair_chart
            st.altair_chart(chart, use_container_width=True)

            num_bins = len(bins_grid)

    # Return the updated DataFrame
    updated_bins_df = pd.DataFrame(bins_grid)
    
    return updated_bins_df, percentage_difference, num_bins

def effect_size_question(jsonfile_name):
    col1, col2= st.columns(2)
    with col1:
        st.markdown(jsonfile_name['effect_size'])
        st.number_input('Click to increase and decrease the counter or directly insert the number.', min_value=0, max_value=10000, key = jsonfile_name['num_input_question'])


def add_submission(updated_bins_question_1_df, updated_bins_question_2_df, updated_bins_question_3_df, updated_bins_question_4_df, updated_bins_question_5_df, updated_bins_question_6_df, updated_bins_question_7_df):
    
    updated_bins_list = [updated_bins_question_1_df, updated_bins_question_2_df, updated_bins_question_3_df, updated_bins_question_4_df, updated_bins_question_5_df, updated_bins_question_6_df, updated_bins_question_7_df]
    
    transposed_bins_list = [df.transpose() for df in updated_bins_list]
    
    # Extracting the first row of each transposed dataframe as column names
    column_names_list = [list(transposed_df.iloc[0]) for transposed_df in transposed_bins_list]

    # Setting the column names for each dataframe
    for i, transposed_df in enumerate(transposed_bins_list):
        transposed_df.columns = column_names_list[i]

    # Removing the first row (used as column names) from each dataframe
    transposed_bins_list = [transposed_df.iloc[1:] for transposed_df in transposed_bins_list]

    # Adding prefix to column names of each dataframe
    for i, transposed_df in enumerate(transposed_bins_list):
        prefix = f'Q{i + 1}  '
        transposed_df.columns = [f'{prefix}{col}' for col in transposed_df.columns]

    # Concatenating transposed dataframes
    questions_df = pd.concat(transposed_bins_list, axis=1)

    # Resetting index if needed
    questions_df.reset_index(drop=True, inplace=True)

    # Update session state
    data = st.session_state['data']

    USER_FULL_NAME = 'User Full Name'
    USER_PROF_CATEGORY = 'User Professional Category'
    USER_POSITION = 'User Working Position'
    YEARS_OF_EXPERIENCE = 'User Years of Experience'
    MIN_EFF_SIZE_Q1 = 'Minimum Effect Size Q1'
    MIN_EFF_SIZE_Q2 = 'Minimum Effect Size Q2'
    MIN_EFF_SIZE_Q3 = 'Minimum Effect Size Q3'
    MIN_EFF_SIZE_Q6 = 'Minimum Effect Size Q6'
    MIN_EFF_SIZE_Q7 = 'Minimum Effect Size Q7'


    data[USER_FULL_NAME].append(safe_var('user_full_name'))
    data[USER_POSITION].append(safe_var('user_position'))
    data[USER_PROF_CATEGORY].append(safe_var('professional_category'))
    data[YEARS_OF_EXPERIENCE].append(safe_var('years_of_experience'))
    data[MIN_EFF_SIZE_Q1].append(safe_var('num_input_question1'))
    data[MIN_EFF_SIZE_Q2].append(safe_var('num_input_question2'))
    data[MIN_EFF_SIZE_Q3].append(safe_var('num_input_question3'))
    data[MIN_EFF_SIZE_Q6].append(safe_var('num_input_question6'))
    data[MIN_EFF_SIZE_Q7].append(safe_var('num_input_question7'))


    st.session_state['data'] = data
    
    session_state_df = pd.DataFrame(data)
    personal_data_df = session_state_df.iloc[:, :4]
    min_eff_df = session_state_df.iloc[:, 4:]
    st.write(personal_data_df)
    st.write(min_eff_df)
    st.write(questions_df)
    
    concatenated_df = pd.concat([personal_data_df, questions_df.set_index(personal_data_df.index), min_eff_df.set_index(personal_data_df.index)], axis=1)
    
    st.session_state['submit'] = True
    #save data to google sheet
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(secrets_to_json(), scope)
    client = gspread.authorize(creds)
 
    sheet = client.open("Survey answers: Romania Case").sheet1

    column_names_list = concatenated_df.columns.tolist()
    #test_sheet = client.create(f'Test for Romania').sheet1
    #column_names = sheet.append_row(column_names_list)
    sheet_row_update = sheet.append_rows(concatenated_df.values.tolist()) #.values.tolist())
    #duplicate = sheet.duplicate(new_sheet_name='Duplicate data')
    #st.success('Data has been saved successfully.')
    
    #Navigate to the folder in Google Drive. Copy the Folder ID found in the URL. This is everything that comes after “folder/” in the URL.
    backup_sheet = client.create(f'Backup_{data[USER_FULL_NAME]}_{datetime.now()}', folder_id='1WTHKA2QT-1MDj0PpV5YX_Yboxf4pniJ9').sheet1
    backup_sheet = backup_sheet.append_rows(concatenated_df.values.tolist()) #(new_bins_df.iloc[:2].values.tolist())
    #backup_sheet.share('', perm_type = 'user', role = 'writer')

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')
