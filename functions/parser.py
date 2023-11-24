# import config
from functions.config import *

# import libraries
import os
from bs4 import BeautifulSoup
from tqdm.notebook import tqdm
import csv

def html_extraction():
    '''
    This function open one by one all the html files and extract all the useful informations we need from them.
    Extracted informations are then saved in .tsvs files
    We avoid repeating extractions if files are already present.
    We notice that some fields are always present while others are not. Those two kinds are treated differently
    
    Args:
        - None

    Returns:
        - None

    '''

    # create folder if not exist already
    if not os.path.exists(tsvs_path):
        os.makedirs(tsvs_path)

    # we check if all the files already exists, in this case we do not repeat the crawling
    to_crawl = False
    files_count = 0
    for _, _, files in os.walk(tsvs_path):
        files_count += len(files)

    if files_count < n_courses:
        print("Creating .tsv files...")
        to_crawl = True
    else:
        print("All files already created. Using the existing version.")

    # if data is missing go crawl
    if to_crawl == True:
        with open(courses_urls_path, 'r') as courses_file:
            for i, url in tqdm(enumerate(courses_file), total = n_courses):
                url = url.strip("\n")

                # if file .tsv already exist skip its creation
                tsv_file_path = tsvs_path + "course_" + str(1 + i) + ".tsv"
                if os.path.exists(tsv_file_path):
                    continue

                # create path, open and read .html file
                course_file_path = courses_pages_path + "page_" + str(1 + i // courses_per_page) + "/" + "course_" + str(1 + i % courses_per_page) + ".html"
                with open(course_file_path, 'r', encoding = "utf-8") as html_file:
                    html_content = html_file.read()

                soup = BeautifulSoup(html_content, "html.parser")

                # if the page is no avaiable we can't get informations
                if soup.title.text == r"FindAMasters | 500 Error : Internal Server Error":
                    courseName = universityName = facultyName = isItFullTime = description = startDate = fees = modality = duration = city = country = administration = ""

                else:
                    # get all the required fields

                    courseName = soup.find("h1", {"class": "course-header__course-title"}).get_text(strip = True, separator = " ")
                    universityName = soup.find("a", {"class": "course-header__institution"}).get_text(strip = True, separator = " ")
                    facultyName = soup.find("a", {"class": "course-header__department"}).get_text(strip = True, separator = " ")

                    # some entries do not have this field
                    extract = soup.find("span", {"class": "key-info__study-type"})
                    if extract is None:
                        isItFullTime = ""
                    else:
                        isItFullTime = extract.get_text(strip = True, separator = " ")

                    description = soup.find("div", {"class": "course-sections__description"}).find("div", {"class": "course-sections__content"}).get_text(strip = True, separator = " ")
                    startDate = soup.find("span", {"class": "key-info__start-date"}).get_text(strip = True, separator = " ")

                    # some entries do not have this field
                    extract = soup.find("div", {"class": "course-sections__fees"})
                    if extract is None:
                        fees = ""
                    else:
                        fees = extract.find("div", {"class": "course-sections__content"}).get_text(strip = True, separator = " ")

                    modality = soup.find("span", {"class": "key-info__qualification"}).get_text(strip = True, separator = " ")
                    duration = soup.find("span", {"class": "key-info__duration"}).get_text(strip = True, separator = " ")
                    city = soup.find("a", {"class": "course-data__city"}).get_text(strip = True, separator = " ")
                    country = soup.find("a", {"class": "course-data__country"}).get_text(strip = True, separator = " ")

                    # courses can be 'on_campus', 'online' or both, but this information is stored in different tags
                    extract1 = soup.find("a", {"class": "course-data__online"})
                    extract2 = soup.find("a", {"class": "course-data__on-campus"})
                    if extract1 is None and extract2 is None:
                        administration = ""
                    elif extract2 is None:
                        administration = extract1.get_text(strip = True, separator = " ")
                    elif extract1 is None:
                        administration = extract2.get_text(strip = True, separator = " ")
                    else:
                        administration = extract1.get_text(strip = True, separator = " ") + " & " + extract2.get_text(strip = True, separator = " ")

                data = [["courseName", "universityName", "facultyName", "isItFullTime", "description", "startDate", "fees", "modality", "duration", "city", "country", "administration", "url"],
                        [courseName, universityName, facultyName, isItFullTime, description, startDate, fees, modality, duration, city, country, administration, url]]

                with open(tsv_file_path, 'w+', newline='') as tsv_file:
                    writer = csv.writer(tsv_file, delimiter = '\t', lineterminator = '\n')
                    writer.writerows(data)