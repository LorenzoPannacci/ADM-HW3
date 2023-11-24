# config.py

# path to the folder that contains all the data
global data_folder_path
data_folder_path = r"data/"


# file path of the .txt file to create
global courses_urls_path
courses_urls_path = data_folder_path + r"courses_urls.txt"

# number of pages to search trough
global n_pages
n_pages = 400

# total number of courses crawled
global courses_per_page
courses_per_page = 15

# total number of courses crawled
global n_courses
n_courses = n_pages * courses_per_page

# path of the folder containing all the subfolders with the html files
global courses_pages_path
courses_pages_path = r"data/courses_html_pages/"

# path of the folder containing all the .tsv files
global tsvs_path
tsvs_path = r"data/tsvs/"

# path of the vocabulary file
global vocabulary_file_path
vocabulary_file_path = r"data/vocabulary.txt"

# path of the inverted index file
global inv_index_file_path
inv_index_file_path = r"data/inverted_index.txt"

# path of the inverted index tfidf file
global inv_ind_tfidf_file_path
inv_ind_tfidf_file_path = r"data/inv_index_tfidf.txt"

# path of the coordinates table
global coordinates_table_path
coordinates_table_path = r"data/coordinates_table.csv"