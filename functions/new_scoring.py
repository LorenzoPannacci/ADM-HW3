# import config
from functions.config import *
from functions import engine

# import libraries
import pandas as pd
import heapq

def parse_start_date(start_date):
    '''
    Convert 'start_date' string into numbers representing the months.
    '''

    #seperate the months in the string
    months = start_date.split(', ')
    
    try:
        # convert month names to their numerical representation
        month_numbers = [pd.to_datetime(month.strip(), format='%B').month for month in months]
        return month_numbers
    except ValueError:
        return []  # return an empty list for invalid dates such as "See Course", "Any Month"

def calculate_start_date_score(start_date):
    '''
    The following function is used to assess document scores based on their start date, confronting it with the **current date**.
    It extracts the starting months from the startDate column and determines the time remaining (monthly) for the course to start.
    Subsequently, it returns 1 if the course is starting in the next 3 months and 0.5 if it starts in the next 6 months.
    '''
    
    # if the course starts any month it is an advantage it should get higher score
    if start_date=="Any Month": 
        return 1
    
    # to eliminate the courses already started we need to find monthly difference between current month and start dates
    current_month = pd.to_datetime('today').month
    start_months = parse_start_date(start_date)
   
    if not start_months:
        return -1  # return -1 if no valid months are found ("See course page")
    
    # find the closest future month
    # to find the closest month among the list we need to select the minimum difference. 
    closest_future_month = min(((month - current_month) % 12) for month in start_months) 

    months_difference = closest_future_month
    if months_difference < 3: # the course starts very soon it is an advantage it should get high score
        return 1
    elif months_difference < 6: # the course starts rather late, it should get medium score
        return 0.5
    else:                     # the course will not be starting any time soon, it is a disadvantage it should get negative score
        return -1

def scoring_function(query, vocabulary, inverted_index, inverted_index_tfidf, k = 5, all_columns = False):
    # create necessary dataframes
    result_df = engine.search_engine(query, vocabulary, inverted_index, all_rows = True)
    similarities_scores = engine.top_k_documents(query, vocabulary, inverted_index, inverted_index_tfidf, k = "all")

    # use a heap to maintain the top-k documents
    heap = []
    for _, row in result_df.iterrows():
        
        # score based on the presence of the query in that spesific order in the description
        if engine.preprocess_text(query) in engine.preprocess_text(row['description']):
            score_description = similarities_scores[similarities_scores["url"] == row["url"]]["similarityScore"].item()
        else:
            # we use 'url' as unique identifier
            score_description = similarities_scores[similarities_scores["url"] == row["url"]]["similarityScore"].item()
       
        # score based on the presence of any part of the query in the course name
        score_course_name = any(word in engine.preprocess_text(row['courseName']) for word in engine.preprocess_text(query).split())
        
        # score based on the presence of empty rows
        if (row.isnull().any().any() or row.isna().any().any() or (type(row['fees (EUR)']) == type("") and row['fees (EUR)'] == "") or (type(row['fees (EUR)']) == type(pd.Series()) and row['fees (EUR)'].empty)):
            score_empty_info = -1
        else:
            score_empty_info = 1
        
        # score based on the proximity of the start date to the current month
        score_start_date = calculate_start_date_score(row['startDate'])
        
        # score based on the presence of both online and on-campus options in the "administration" field
        score_administration = 1 if 'Online & On Campus' in row['administration'] else 0
        
        # score based on the presence of both part time and full time options in the "isItFullTime" field
        score_isitfulltime = 1 if 'Full time&Part time' in row['isItFullTime'] else 0
        
        # calculate the score for the current row
        total_score = (
            0.5 * score_description +
            0.1 * score_course_name +
            0.2 * score_start_date +
            0.1 * score_empty_info +
            0.05 * score_administration +
            0.05 * score_isitfulltime
        )

        # we should store the top_k elements as a heap structure
        # if the heap is not full, add the current row
        if len(heap) < k:
            heapq.heappush(heap, (total_score, row['courseName'], row['universityName'], row['city'], row['country'], row['description'], row['fees (EUR)'], row['url']))
        else:
            # if the current score is greater than the smallest score in the heap, replace the smallest score
            if total_score > heap[0][0]:
                heapq.heappop(heap)
                heapq.heappush(heap, (total_score, row['courseName'], row['universityName'], row['city'], row['country'], row['description'], row['fees (EUR)'], row['url']))

    # sort the heap in descending order
    heap.sort(reverse=True)

    # create a DataFrame from the heap
    if all_columns:
        top_k_df = pd.DataFrame(heap, columns=['total_score', 'courseName', 'universityName', 'city', 'country', 'description', 'fees (EUR)', 'url'])
    else:
        top_k_df = pd.DataFrame(heap, columns=['total_score', 'courseName', 'universityName', 'description', 'url'])

    return top_k_df
