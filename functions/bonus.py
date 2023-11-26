# import config
from functions.config import *
from functions import engine

# import libraries
import pandas as pd
import os
from tqdm.notebook import tqdm
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import heapq
    
def generalized_create_vocabulary(t):
    '''
    Works the same as the one described in 'engine.py' but generalized for all the fields needed in question 5.
    '''

    print("Creating vocabulary type " + str(t) + "..." )

    # start an empty dictionary
    vocabulary = {}

    # start with term_id as 1
    term_id = 1

    for i in tqdm(range(1, n_courses + 1)):
        tsv="course_"+str(i)+".tsv"
        file_path= os.path.join(data_folder_path + "tsvs",tsv)
        with open(file_path, 'r', encoding='utf-8') as ff:
            lines=ff.readlines()
        
        fields = lines[1].strip().split('\t')
        # ensure that the list has enough elements
        if len(fields) > 4:
            
            # preprocess the feature (1:description 2:course name 3:university name 4:university city) according to input choice
            if t==1:
                d=engine.preprocess_text(fields[4])
            elif t==2:
                d=engine.preprocess_text(fields[0])
            elif t==3:
                d=engine.preprocess_text(fields[1])
            elif t==4:
                d=engine.preprocess_text(fields[-4])
                
            # tokenize 
            words=d.split()
            
            for w in words:
                if w not in vocabulary: #add to the vocabulary if the word is not in there yet
                    vocabulary[w]=term_id #assigns a unique id
                    term_id+=1 # update term_id

    # save the vocabulary to a file
    vocabulary_file_path = data_folder_path + "vocabulary_type" + str(t) + ".txt"
    with open(vocabulary_file_path, 'w', encoding='utf-8') as vocab:
        for word, term_id in vocabulary.items():
            vocab.write(f"{word}\t{term_id}\n")

def generalized_load_vocabulary(file_path):
    '''
    The same as the one described in 'engine.py'
    '''

    vocabulary = {}

    with open(file_path, 'r') as file:
        # read each line in the file
        for line in file:
            # split the line by tab
            parts = line.strip().split('\t')
            name, number = parts
            vocabulary[name] = int(number)
    
    return vocabulary

def generalized_create_inverted_index(vocabulary, t):
    '''
    Works the same as the one described in 'engine.py' but generalized for all the fields needed in question 5.
    '''

    print("Creating inverted index type " + str(t) + "..." )
    # initialize an empty inverted_index
    inverted_index={}

    for i in tqdm(range(1, n_courses + 1)):
        tsv="course_"+str(i)+".tsv"
        file_path= os.path.join(tsvs_path,tsv)
        with open(file_path, 'r', encoding='utf-8') as ff:
            lines=ff.readlines()
        
        fields = lines[1].strip().split('\t')
        # ensure that the list has enough elements
        if len(fields) > 4:
            # access the description field and tokenize the words,

            if t==1:
                d=engine.preprocess_text(fields[4])
            elif t==2:
                d=engine.preprocess_text(fields[0])
            elif t==3:
                d=engine.preprocess_text(fields[1])
            elif t==4:
                d=engine.preprocess_text(fields[-4])

            words=d.split()
            for w in words:
                # check if the word contains alphabetical characters or numbers
                if w in vocabulary:
                    # update inverted index
                    id_term = vocabulary[w]
                    if id_term not in inverted_index:
                        inverted_index[id_term]=[tsv]
                    else:
                        if(tsv not in inverted_index[id_term]):
                            inverted_index[id_term].append(tsv)


    # save the inverted index in a file
    inv_index_file_path = data_folder_path + "inv_index_type" + str(t) + ".txt"
    with open(inv_index_file_path, 'w', encoding='utf-8') as inv_ind:
        for word, term_id in inverted_index.items():
            inv_ind.write(f"{word}\t{term_id}\n")

def generalized_create_inverted_index_tfidf(vocabulary, t):
    '''
    Works the same as the one described in 'engine.py' but generalized for all the fields needed in question 5.
    '''

    print("Creating inverted index type " + str(t) + "..." )
    # initialize the inverted index with tf-idf scores 
    inv_index_tfidf = {}
    # initialize dictionaries for term frequency (t_f) and document frequency (d_f)
    t_f = {}
    d_f = {}

    # step 1: calculate term frequency (tf) and inverse document frequency (idf)
    for i in tqdm(range(1, n_courses + 1)):
        tsv="course_"+str(i)+".tsv"
        file_path= os.path.join(tsvs_path,tsv)
        with open(file_path, 'r', encoding='utf-8') as ff:
            lines=ff.readlines()
        
        # extract the fields from the second line
        fields = lines[1].strip().split('\t')
        
        # ensure that the list has enough elements
        if len(fields) > 4:
            # access the description field and tokenize the words,

            if t==1:
                words=engine.preprocess_text(fields[4]).split()
            elif t==2:
                words=engine.preprocess_text(fields[0]).split()
            elif t==3:
                words=engine.preprocess_text(fields[1]).split()
            elif t==4:
                words=engine.preprocess_text(fields[-4]).split()            

            # calculate term frequency (tf) for each term in the document
            for w in words:
                term_id = vocabulary.get(w)
                if term_id:
                    # if the pair doesn't exist  it is initialized with a count of 0 before incrementing.
                    # If the pair already exists, it doesn't override the existing value; 
                    # it simply returns the existing value associated with that key.
                    t_f.setdefault((term_id, tsv), 0) 
                    t_f[(term_id, tsv)] += 1

            # update document frequency for each term
            seen_words = set()
            for word in set(words):
                term_id = vocabulary.get(word)
                if term_id and term_id not in seen_words:
                    d_f.setdefault(term_id, 0)
                    d_f[term_id] += 1
                    seen_words.add(term_id)

    # step 2: calculate tf-idf and build the inverted index
    for (term_id, doc_id),tf in t_f.items():
        
        # calculate inverse document frequency (idf)
        idf = np.log(n_courses/ (d_f[term_id] + 1))  
        # calculate tf-idf score
        tfidf = np.round(tf * idf,2)
        
        # update the inverted index with the term_id and the corresponding tuple
        inv_index_tfidf.setdefault(term_id, [])
        inv_index_tfidf[term_id].append((doc_id, tfidf))

    # save the inverted index in a file
    inv_ind_tfidf_file_path = data_folder_path + "inv_index_tfidf_type" + str(t) + ".txt"
    with open(inv_ind_tfidf_file_path, 'w', encoding='utf-8') as tfidf:
        for word, term_id in inv_index_tfidf.items():
            tfidf.write(f"{word}\t{term_id}\n")

def generalized_load_inverted_index(file_path):   
    '''
    The same as the one described in 'engine.py'
    '''

    inverted_index = {}

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip().split('\t')
            key = int(line[0])
            value = eval(line[1])
            inverted_index[key] = value

    return inverted_index

def get_query_dataframe(t, query):
    '''
    Given a query in one of the fields requested by question 5, return a dataframe containing only relevant courses and their
    score calculated on the query in the corresponding field. It's a generalized version of the 'get_top_k' functions written
    in 'engine.py'.
    '''

    # get paths
    vocabulary_path = data_folder_path + "vocabulary_type" + str(t) + ".txt"
    inverted_index_path = data_folder_path + "inv_index_type" + str(t) + ".txt"
    inverted_index_tfidf_path = data_folder_path + "inv_index_tfidf_type" + str(t) + ".txt"

    # create and load components
    if not os.path.exists(vocabulary_path):
        generalized_create_vocabulary(t)
    vocabulary = generalized_load_vocabulary(vocabulary_path)

    if not os.path.exists(inverted_index_path):
        generalized_create_inverted_index(vocabulary, t)
    inverted_index = generalized_load_inverted_index(inverted_index_path)

    if not os.path.exists(inverted_index_tfidf_path):
        generalized_create_inverted_index_tfidf(vocabulary, t)
    inverted_index_tfidf = generalized_load_inverted_index(inverted_index_tfidf_path)

    # preprocess and tokenize the query
    query_words = engine.preprocess_text(query)
    
    # vectorize the query
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform([query_words])
    query_vector = X.toarray()[0]

    # tokenize the query
    query_words=query_words.split()
    
    ############################
    # get all useful documents #
    ############################

    doc = set()
    for i in range(len(query_words)):
        tmp=set() 
        w = query_words[i]
        if w in vocabulary:
            term_id = vocabulary[w]
            if term_id in inverted_index:
                t_id=inverted_index[term_id]
                if i==0:
                    doc.update(t_id)
                else:
                    tmp.update(t_id)
        if i>0:
            doc=doc.intersection(doc, tmp)    

    ##############
    # get scores #
    ##############

    heap = []
    for doc_id in doc:
        doc_vector = {}
        # aggregate tf-idf scores for each term in the document
        for term_id, tfidf in inverted_index_tfidf.items():
            for doc, score in tfidf:
                if doc == doc_id:
                    doc_vector[term_id] = score

        # calculate the cosine similarity
        prod = 0.0
        for i in range(len(query_vector)):
            prod += query_vector[i] * doc_vector[vocabulary[query_words[i]]] 
        norm_doc = np.linalg.norm(np.array(list(doc_vector.values()))) 
        norm_query = np.linalg.norm(query_vector) 
        if norm_doc != 0 and norm_query != 0:
            score = prod / (norm_doc * norm_query)
        
        # add the document information and similarity score to the heap
        heapq.heappush(heap, (-score, doc_id))

    ######################
    # creating dataframe #
    ######################
    
    result_documents = []
    for i in range(len(heap)):
        similarity_score, doc_id = heapq.heappop(heap)
        
        tsv_file = os.path.join(tsvs_path, f"{doc_id}")
        with open(tsv_file, 'r', encoding='utf-8') as ff:
            lines=ff.readlines()
        fields=lines[1].split("\t")
        result_documents.append({
                    'courseName': fields[0],
                    'universityName': fields[1],
                    'isItFullTime': fields[3],
                    'description': fields[4],
                    'startDate': fields[5],
                    'fees (EUR)': fields[7],
                    'city': fields[10],
                    'country': fields[11],
                    'administration': fields[-2],
                    'url': fields[-1],
                    'similarityScore_type' + str(t): -similarity_score  # Convert back to positive
        })
            
    # return pandas DataFrame
    return pd.DataFrame(result_documents)

def calculate_start_date_difference(start_date):
    try:
        #seperate the months in the string
        months = start_date.split(', ')
    
        # convert month names to their numerical representation
        start_months = [pd.to_datetime(month.strip(), format='%B').month for month in months]

        current_month = pd.to_datetime('today').month
        
        if not start_months:
            return 12
        
        # find the closest future month
        # to find the closest month among the list we need to select the minimum difference. 
        closest_future_month = min(((month - current_month) % 12) for month in start_months) 

        months_difference = closest_future_month

        return months_difference

    except:
        return 12

def bonus_search_engine(input_dict):
    '''
    The user have chosen a feature to conduct the serching process by assigning a number to search_engine variable.
    (1:description 2:course name 3:university name 4:university city)
    The vocabulary and inverted index files created according to the chosen feature
    The 1st part of the bonus question completed in here
    For the 2nd, 3rd, 4th and 5th parts of the bonus question we need to make filtering. 
    The filtering process will be conducted in the search_engine_bonus function
    '''

    description_query = input_dict["description_query"]
    df1 = get_query_dataframe(1, description_query)

    advanced_search_engine = input_dict["advanced_search_engine"]
    if advanced_search_engine:
        # we get courses relevant to all the queries by doint intersections of the dataframes obtained singularly on the single queries

        course_name_query = input_dict["course_name_query"]
        df2 = get_query_dataframe(2, course_name_query)
        if df2.empty:
            print("No courses found!")
            return
        df1 = pd.merge(df1, df2, on=['courseName', 'universityName', 'isItFullTime', 'description', 'startDate', 'fees (EUR)', 'city', 'country', 'administration', 'url'], how='inner')

        university_name_query = input_dict["university_name_query"]
        df3 = get_query_dataframe(3, university_name_query)
        if df3.empty:
            print("No courses found!")
            return
        df1 = pd.merge(df1, df3, on=['courseName', 'universityName', 'isItFullTime', 'description', 'startDate', 'fees (EUR)', 'city', 'country', 'administration', 'url'], how='inner')

        university_city_query = input_dict["university_city_query"]
        df4 = get_query_dataframe(4, university_city_query)
        if df4.empty:
            print("No courses found!")
            return
        df1 = pd.merge(df1, df4, on=['courseName', 'universityName', 'isItFullTime', 'description', 'startDate', 'fees (EUR)', 'city', 'country', 'administration', 'url'], how='inner')

    # then we apply the filters

    use_fee_filter = input_dict["use_fee_filter"]
    if use_fee_filter:
        # remove those without fees
        df1["fees (EUR)"] = pd.to_numeric(df1["fees (EUR)"], errors='coerce')
        df1 = df1.dropna(subset=["fees (EUR)"])

        # search between range
        min_fee = input_dict["min_fee"]
        max_fee = input_dict["max_fee"]
        df1 = df1[(df1["fees (EUR)"] >= min_fee) & (df1["fees (EUR)"] <= max_fee)]
    
    use_country_filter = input_dict["use_country_filter"]
    if use_country_filter:
        country_list = input_dict["country_list"]
        df1 = df1[df1["country"].isin(country_list)]

    use_start_filter = input_dict["use_start_filter"]
    if use_start_filter:
        df1 = df1[(df1["startDate"].apply(calculate_start_date_difference).between(0, 6)) | (df1['startDate'] == "Any Month")]

    use_online_filter = input_dict["use_online_filter"]
    if use_online_filter:
        df1 = df1.dropna(subset=["administration"])
        df1 = df1[df1["administration"].str.contains('Online')]
    
    if advanced_search_engine:
        df1["advanced_score"] = (df1["similarityScore_type1"] + df1["similarityScore_type2"] + df1["similarityScore_type3"] + df1["similarityScore_type4"]) / 4
        df1 = df1.drop(["similarityScore_type1", "similarityScore_type2", "similarityScore_type3", "similarityScore_type4"], axis = 1)
    else:
        df1["advanced_score"] = df1["similarityScore_type1"]
        df1 = df1.drop(["similarityScore_type1"], axis = 1)

    # finally we drop non requested columns and return the dataframe

    df1 = df1.drop(["isItFullTime", "description", "startDate", "fees (EUR)", "city", "country", "administration"], axis = 1)

    return df1