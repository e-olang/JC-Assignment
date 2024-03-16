import pandas as pd
from datetime import datetime


def read_cases(original_df):
    # List to store new data frames for each row i.e. each case
    cases = []

    # Iterate through each row in the original DataFrame
    for index, row in original_df.iterrows():
        # Create a new case df for the current row
        case = pd.DataFrame([row], columns=original_df.columns)
        # Append the new case to the list
        cases.append(case)
    
    return cases    # a list of df, which can then be processed individually for loading into DB.


def create_case(case_df, instances = 4):
    data = case_df.copy()
    data = data.dropna(axis = 1, how = 'all')   # drop any empty columns from current case
    
    # process facility columns to fetch facility code and facility name
    copydf = data.copy()
    # Find the column starting with 'mentor_checklist/mentor/q_facility'
    facility_column = next((col for col in copydf.columns if col.startswith('mentor_checklist/mentor/q_facility')), None)
    facility_data = ' '.join(copydf[facility_column].astype(str))
    code, name = facility_data.split('_', 1)
    
    copydf['facility_code'] = code
    copydf['facility_name'] = name.replace('_', ' ')
    copydf.drop(facility_column, axis=1, inplace=True)
    
    
    # Mapping
    # map items from case input to case output. This part handles all the common items i.e. duplicate cells like 
    # mentor names, county, facility details, date, etc.
    # Also makes copies. since a case generates mulitple instamnces depending on number of participants, 
    # we map each participant to 4 instances i.e.: "Each participant completed 4 topics"

    row = copydf.iloc[0]
    
    # Define mapping between column names in df and columns in X
    column_mapping = {
        'id': '_id',
        'cme_completion_date': 'mentor_checklist/cme_grp/cme_completion_date',
        'county': 'mentor_checklist/mentor/q_county',
        'date_submitted': '_submission_time',
        'facility_code': 'facility_code',
        'facility_name': 'facility_name',
        'mentor_name': 'mentor_checklist/mentor/name',
        'submission_id': '_id',
        'success_story': None
    }
    
    mapped_values = {}
    
    for col_X, col_df in column_mapping.items():
        if col_df in row.index:
            mapped_values[col_X] = row[col_df]
            
    blank_keys = [
        'cme_topic', 'cme_unique_id', 'drill_topic', 'drill_unique_id', 'essential_cme_topic',
        'essential_drill_topic', 'id_number_cme', 'id_number_drill', 'success_story'
    ]
    for key in blank_keys:
        mapped_values[key] = None


    keys_to_check = [
        'id', 'county', 'date_submitted', 'cme_completion_date',
        'facility_code', 'facility_name', 'mentor_name', 'submission_id'
    ]
    for key in keys_to_check:
        if key not in mapped_values:
            mapped_values[key] = None
    '''
    if 'cme_completion_date' not in mapped_values:
        mapped_values['cme_completion_date'] = None
    '''
    dataframe_rows = [mapped_values.copy() for _ in range(instances)]
    
    return dataframe_rows



# Handle Missing Cell Per Column:
# 1 Missing dates: CME Completion Date e.g. Case 3 in test file: Kilifi County
def extract_date(date_str):
    # Parse the date string from date submitted (timestamp format) then convert to dat format
    date_object = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
    date_only = date_object.date()
    formatted_date = date_only.strftime('%Y-%m-%d')
    return formatted_date