# import config
from functions.config import *

# import libraries
import re
import nltk
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
import requests
import numpy as np
from tqdm.notebook import tqdm
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import heapq

def preprocess_text(txt):
    '''
    The function takes a text string as input and returns a preprocessed version of the text.
    It utilizes regular expressions to remove all punctuation from the input text.
    After this punctuation removal, the text is tokenized by splitting it into words.
    Stopwords, common words that often don't contribute much to the meaning, are then removed from the tokenized text.
    The function employs stemming using the Porter Stemmer to reduce words to their root form, helping to consolidate similar words.
    Finally, the preprocessed words are joined back together into a single string, creating the final output.
    '''
    
    # remove all punctuation
    txt = re.sub(r'[^\w\s]', ' ', txt)

    # tokenize the text
    txt=txt.split()
    
    # remove stopwords
    stop_words = set(stopwords.words('english'))
    txt = [t for t in txt if t not in stop_words]
 
    # stemming
    stemmer = PorterStemmer()
    txt = [stemmer.stem(t) for t in txt]
 
    # Reassemble the text
    txt = ' '.join(txt)

    return txt

def convert_to_eur(fees):
    '''
    This function takes as input a string of text. It starts by finding the currency symbol.
    The text is previously transformed into its uppercase form to simplify the search.
    We then search for all possible fees and choose the highest one found.
    If both are found, we use the Open Exchange Rates API to convert the currency to Euros.
    Throughout the text, we might find various ways in which the value and currency appear.
    Sometimes, they will be properly separated by a space bar, while other times both parameters will be joined together.
    We will consider both of these cases. Also, the value might appear before or after the currency.
    Finally, for the dollar, pounds, and euros currencies, there are more ways in which they can appear.
    For this special case, we created a special dictionary that will help translate them into the correct form.
    So, when we apply the request function to the website, we will have the correct parameters for these currencies.
    '''

    # remove decimals
    pattern = r'\.00(?![0-9])'
    fees = re.sub(pattern, '', fees)
    
    # uppercase the text & tokenize the text 
    fees=fees.upper().split()
    # removes all commas and points
    fees=[i.replace(',', '').replace('.', '') for i in fees]

    # dict of possible symbols used for dollar, pounds and euros
    # in case one of these keys appears we need to change them into their respective values 
    # to use the request function
    sym={'£':'GBP','POUNDS':'GBP','$':'USD','DOLLARS':'USD','€':'EUR','EUROS':'EUR'}
    # list of all the possible currencies
    curr=["£","POUNDS","GBP","$","DOLLARS","USD","€","EUROS","EUR","AED","AFN","ALL","AMD","ANG","AOA","ARS","AUD","AWG","AZN","BAM","BBD","BDT","BGN","BHD","BIF","BMD","BND","BOB","BRL","BSD","BTN","BWP","BYN","BZD","CAD","CDF","CHF","CLP","CNY","COP","CRC","CUP","CVE","CZK","DJF","DKK","DOP","DZD","EGP","ERN","ETB","FJD","FKP","FOK","GEL","GGP","GHS","GIP","GMD","GNF","GTQ","GYD","HKD","HNL","HRK","HTG","HUF","IDR","ILS","IMP","INR","IQD","IRR","ISK","JEP","JMD","JOD","JPY","KES","KGS","KHR","KID","KMF","KRW","KWD","KYD","KZT","LAK","LBP","LKR","LRD","LSL","LYD","MAD","MDL","MGA","MKD","MMK","MNT","MOP","MRU","MUR","MVR","MWK","MXN","MYR","MZN","NAD","NGN","NIO","NOK","NPR","NZD","OMR","PAB","PEN","PGK","PHP","PKR","PLN","PYG","QAR","RON","RSD","RUB","RWF","SAR","SBD","SCR","SDG","SEK","SGD","SHP","SLE","SLL","SOS","SRD","SSP","STN","SYP","SZL","THB","TJS","TMT","TND","TOP","TRY","TTD","TVD","TWD","TZS","UAH","UGX","UYU","UZS","VES","VND","VUV","WST","XAF","XCD","XDR","XOF","XPF","YER","ZAR","ZMW","ZWL"]
    
    # find value and currency
    v=[] # list of values
    c=[] # list of currencies
    for i,elem in enumerate(fees):
        if elem.isdigit():
            # check if there is a currency used before the digit
            if i>0 and fees[i-1] in curr:
                v.append(float(elem))
                if (fees[i-1] in sym):
                    c.append(sym[fees[i-1]])
                else:
                    c.append(fees[i-1])
            elif i<len(fees)-1 and fees[i+1] in curr:
                # check if there is a currency used after the digit
                v.append(float(elem))
                if (fees[i+1] in sym): 
                    c.append(sym[fees[i+1]])
                else:
                    c.append(fees[i+1])
        # check if the currency and the value are attached together as a same element
        elif len(elem)>0 and elem[len(elem)-1] in sym:
            val = re.findall(r"\d+",elem[:len(elem)])
            if val:
                v.append(float(val[0]))
                c.append(sym[elem[len(elem)-1]])
        elif len(elem)>0 and elem[0] in sym:
            val = re.findall(r"\d+",elem[1:len(elem)])
            if val:
                v.append(float(val[0]))
                c.append(sym[elem[0]])

    conv="0.0"
    
    if len(c)>0:
        base_url = "https://open.er-api.com/v6/latest"
        API_KEY="6d56fb10262e4f29bef560d4c38fa3f4"
        conv=[]
        # convert all the values into euros 
        for i in range(len(v)):
            params = {'base': c[i], 'apiKey': API_KEY}
            response = requests.get(base_url, params=params)
            rates = response.json().get('rates', {})
            conv.append(np.round(v[i] * rates['EUR'], 2))
        # get the maximum value
        conv=max(conv)
    return conv

def fees_preprocessing():
    '''
    Add to our .tsv files a new column that store a value representing the fee of the course.
    '''

    for i in tqdm(range(1, n_courses + 1)):
        tsv = "course_" + str(i) + ".tsv"
        file_path = os.path.join(tsvs_path, tsv)
        with open(file_path, 'r', encoding='utf-8') as ff:
            lines=ff.readlines()
        
        fields = lines[1].strip().split('\t')
        
        # read the TSV file into a DataFrame
        df = pd.read_csv(file_path, sep='\t')

        # ensure that the list has enough elements to pick correct column
        if len(fields) > 6:
            # get the fee value
            f = convert_to_eur(fields[6])
        else:
            # otherwise placeholder value
            f = "0.0"
        
        # convert
        if f == "0.0":
            f = np.NAN
        else:
            f = float(f)

        if 'fees (EUR)' in df.columns:
            # update value
            df['fees (EUR)'] = f
        else:
            # add a new column in the eighth position
            df.insert(7, 'fees (EUR)', f)

        # save the modified DataFrame back to the same TSV file
        df.to_csv(file_path, sep='\t', index=False)

    print("New 'fees (EUR)' column added to all .tsv files!")

def create_vocabulary():
    '''
    To create the vocabulary, we begin by initializing an empty dictionary.
    For each of the 6000 tsv files, we extract the description field.
    After preprocessing the text, we iterate through each word, checking if it's already in the vocabulary.
    If not, we add it and assign a unique ID. Finally, the vocabulary is saved in a txt file.
    '''

    # start an empty dictionary
    vocabulary = {}
    # start with term_id as 1
    term_id = 1

    for i in tqdm(range(1, n_courses + 1)):
        tsv="course_"+str(i)+".tsv"
        file_path= os.path.join(tsvs_path,tsv)
        with open(file_path, 'r', encoding='utf-8') as ff:
            lines=ff.readlines()
        
        fields = lines[1].strip().split('\t')
        # Ensure that the list has enough elements
        if len(fields) > 4:
            
            # preprocess the description
            d=preprocess_text(fields[4])
            # tokenize 
            words=d.split()
            
            for w in words:
                if w not in vocabulary: #add to the vocabulary if the word is not in there yet
                    vocabulary[w]=term_id #assigns a unique id
                    term_id+=1 # update term_id

    # save the vocabulary to a file
    with open(vocabulary_file_path, 'w', encoding='utf-8') as vocab:
        for word, term_id in vocabulary.items():
            vocab.write(f"{word}\t{term_id}\n")
    
    print("Vocabulary successfully created!")

def load_vocabulary(file_path):
    vocabulary = {}

    with open(file_path, 'r') as file:
        # read each line in the file
        for line in file:
            # split the line by tab
            parts = line.strip().split('\t')
            name, number = parts
            vocabulary[name] = int(number)
    
    return vocabulary

def create_inverted_index(vocabulary):
    # initialize an empty inverted_index
    inverted_index={}

    for i in tqdm(range(1, n_courses + 1)):
        tsv="course_"+str(i)+".tsv"
        file_path= os.path.join(tsvs_path,tsv)
        with open(file_path, 'r', encoding='utf-8') as ff:
            lines=ff.readlines()
        
        fields = lines[1].strip().split('\t')
        # Ensure that the list has enough elements
        if len(fields) > 4:
            # access the description field and tokenize the words,
            d=preprocess_text(fields[4])
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
    with open(inv_index_file_path, 'w', encoding='utf-8') as inv_ind:
        for word, term_id in inverted_index.items():
            inv_ind.write(f"{word}\t{term_id}\n")
    
    print("Inverted index successfully created!")

def load_inverted_index(file_path):
    # works both for inverted index and inverted index tfidf

    inverted_index = {}

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip().split('\t')
            key = int(line[0])
            value = eval(line[1])
            inverted_index[key] = value

    return inverted_index

def search_engine(query, vocabulary, inverted_index, all_rows = False):
    query_words = preprocess_text(query).split()
    # this list will contain all the docs that have the complete query in their description
    doc = set() 
    for i in range(len(query_words)):
        tmp=set() # we will need this to determine if a document contains all the query elements
        w = query_words[i]
        if w in vocabulary:
            term_id = vocabulary[w]
            if term_id in inverted_index:
                t_id=inverted_index[term_id]
                if i==0:
                    doc.update(t_id)
                else:
                    tmp.update(t_id)
       # filters out the documents that don't contain the previous word of the query
        if i>0:
            doc=doc.intersection(doc, tmp)

    # extract information from matching documents
    result_data = []
    for tsv_id in doc:
        tsv_file = os.path.join(tsvs_path, f"{tsv_id}")
        with open(tsv_file, 'r', encoding='utf-8') as ff:
            lines=ff.readlines()
        fields=lines[1].split("\t")
        if all_rows:
            result_data.append({
                        'courseName': fields[0],
                        'universityName': fields[1],
                        'facultyName': fields[2],
                        'isItFullTime': fields[3],
                        'description': fields[4],
                        'startDate': fields[5],
                        'fees': fields[6],
                        'fees (EUR)': fields[7],
                        'modality': fields[8],
                        'duration': fields[9],
                        'city': fields[10],
                        'country': fields[11],
                        'administration': fields[12],
                        'url': fields[13]
            })

        else:
            result_data.append({
                        'courseName': fields[0],
                        'universityName': fields[1],
                        'description': fields[4],
                        'url': fields[-1]
            })

    # create pandas DataFrame
    result_df = pd.DataFrame(result_data)
    return result_df

def create_inverted_index_tfidf(vocabulary):
    # initialize the inverted index with tf-idf scores 
    inv_index_tfidf = {}
    # Initialize dictionaries for term frequency (t_f) and document frequency (d_f)
    t_f = {}
    d_f = {}

    # step 1: Calculate term frequency (tf) and inverse document frequency (idf)
    for i in tqdm(range(1, n_courses + 1)):
        tsv="course_"+str(i)+".tsv"
        file_path= os.path.join(tsvs_path,tsv)
        with open(file_path, 'r', encoding='utf-8') as ff:
            lines=ff.readlines()
        
        # Extract the fields from the second line
        fields = lines[1].strip().split('\t')
        
        # Ensure that the list has enough elements
        if len(fields) > 4:
            # access the description field and tokenize the words, 
            words=preprocess_text(fields[4]).split()

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
    with open(inv_ind_tfidf_file_path, 'w', encoding='utf-8') as tfidf:
        for word, term_id in inv_index_tfidf.items():
            tfidf.write(f"{word}\t{term_id}\n")

    print("Inverted index TF-IDF successfully created!")

def top_k_documents(query, vocabulary, inverted_index, inverted_index_tfidf, k = 5):
    # preprocess and tokenize the query
    query_words = preprocess_text(query)
    
    # vectorize the query
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform([query_words])
    query_vector = X.toarray()[0]

    # tokenize the query
    query_words=query_words.split()
    
    # find documents that contain all words in the query
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

    # calculate cosine similarity for each matching document
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
    
    result_documents = []
    if k == "all":
        # get all documents
        for i in range(len(heap)):
            similarity_score, doc_id = heapq.heappop(heap)
            
            tsv_file = os.path.join(tsvs_path, f"{doc_id}")
            with open(tsv_file, 'r', encoding='utf-8') as ff:
                lines=ff.readlines()
            fields=lines[1].split("\t")
            result_documents.append({
                        'similarityScore': -similarity_score,  # Convert back to positive
                        'courseName': fields[0],
                        'universityName': fields[1],
                        'description': fields[4],
                        'url': fields[-1]
            })

    else:
        # get the top-k documents
        for i in range(min(k,len(heap))):
            similarity_score, doc_id = heapq.heappop(heap)
            
            tsv_file = os.path.join(tsvs_path, f"{doc_id}")
            with open(tsv_file, 'r', encoding='utf-8') as ff:
                lines=ff.readlines()
            fields=lines[1].split("\t")
            result_documents.append({
                        'similarityScore': -similarity_score,  # Convert back to positive
                        'courseName': fields[0],
                        'universityName': fields[1],
                        'description': fields[4],
                        'url': fields[-1]
            })
            
    # return pandas DataFrame
    return pd.DataFrame(result_documents)