#!/bin/bash


#command useful in order to format the output
paint=$(tput rev)
no_paint=$(tput sgr 0)
blue=$(tput setaf 4)
red=$(tput setaf 1)
green=$(tput setaf 2)
yellow=$(tput setaf 3)

#printing formatted title and introduction
echo -e "\n"
echo "$paint$red                      COMMAND LINE QUESTION HW3 AMDM                            $no_paint"
echo "$paint$red  $no_paint                                                                            $paint$red  $no_paint"
echo "$paint$red  $no_paint This bash script merges all the 6000 files .tsv in one and answers to      $paint$red  $no_paint"
echo "$paint$red  $no_paint the three questions by analysing the .tsv file created.                    $paint$red  $no_paint"
echo "$paint$red  $no_paint                                                                            $paint$red  $no_paint"
echo "$paint$red                                                                                $no_paint"
echo -e "\n"
echo "Please wait a few seconds, untill you see the result on standard output, the machine is calculating..."
echo "For a clearly visualization of the output it's recommended to maximize the terminal window..."
echo -e "\n"


#################
#               #
# Merging files #---------------------------------------------------
#               #
#################

#inizialization of the merged_file with the headers
head -n1 course_1.tsv > merged_courses.tsv

#appending rows to the merged_file
for file in course*.tsv
do
    tail -n1 $file >> merged_courses.tsv
done


#################################
#                               #
# Which country and which city? #-----------------------------------
#                               #
#################################

#assegnation of variable useful for calculate the max
max_1=0
max_country=' '

#extracting the countries column 
cut -f11 merged_courses.tsv | sed 1d | sort -u > countries.tsv

#this command says to the for loop to consider the entire line as a variable 
IFS=$'\n'

#for loop along all the countries
for country in $(cat 'countries.tsv')
do
    #l contains the occurrence of the country
    l=$(cut -f11 merged_courses.tsv | grep -i $country | wc -l)
    
    #if statement in order to compare and extract the max
    if [ $l -ge $max_1 ]
    then
	max_1=$l
	max_country=$country
    fi
done

#this part works as the previous
max_2=0
max_city=' '
cut -f10 merged_courses.tsv | sed 1d | sort -u > cities.tsv

IFS=$'\n'
for city in $(cat 'cities.tsv')
do
    c=$(cut -f10 merged_courses.tsv | grep -i $city | wc -l)
    if [ $c -ge $max_2 ]
    then
	max_2=$c
	max_city=$city
    fi
done


####################
#                   #
# Part-time courses #-----------------------------------------------
#                   #
#####################

#extracting the columns of the university name and the time type
cut -f2,4 merged_courses.tsv | sed 1d | grep -i 'part time' | cut -f1 > univ_p-t.tsv

#sorting and deleting the duplicates we can calculate
#the number of university that offers part-time courses
num_univ=$(sort -u univ_p-t.tsv | wc -l)


##########################################
#                                        #
# Calculating the courses in Engineering #--------------------------
#                                        #
##########################################

#extracting the column about the courses' name
cut -f1 merged_courses.tsv | sed 1d > courseName.tsv

#counting the courses with 'Engineer' in their name
x=$(grep -i "Engineer" courseName.tsv | wc -l)

#counting the total courses (not counting the empty lines)
y=$(grep -vc '^$' courseName.tsv)

#calculating the percentage
z=$(echo "scale=3;$x*100.0/$y" | bc)


#removing the temporary files used for the analysis 
rm cities.tsv
rm countries.tsv
rm univ_p-t.tsv
rm courseName.tsv

#printing formatted output question 1
echo "$paint$blue    QUESTION 1: WHICH COUNTRY OFFERS THE MOST MASTER'S DEGREES? WHICH CITY?     $no_paint"
echo "$paint$blue  $no_paint                                                                            $paint$blue  $no_paint"
echo "$paint$blue  $no_paint The country that offers the greater number of Master's Degrees is:         $paint$blue  $no_paint"
echo "$paint$blue  $no_paint "$max_country" with "$max_1" courses.                                          $paint$blue  $no_paint"
echo "$paint$blue  $no_paint The city that offers the greater number of Master's Degree is: "$max_city"      $paint$blue  $no_paint"
echo "$paint$blue  $no_paint with "$max_2" courses                                                          $paint$blue  $no_paint"
echo "$paint$blue  $no_paint                                                                            $paint$blue  $no_paint"
echo "$paint$blue                                                                                $no_paint"

#question 2
echo "$paint$green    QUESTION 2: HOW MANY COLLEGES OFFER PART-TIME EDUCATION?                    $no_paint"
echo "$paint$green  $no_paint                                                                            $paint$green  $no_paint"
echo "$paint$green  $no_paint The number of colleges that offer part-time education is: "$num_univ"              $paint$green  $no_paint"
echo "$paint$green  $no_paint                                                                            $paint$green  $no_paint"
echo "$paint$green                                                                                $no_paint"

#question 3
echo "$paint$yellow    QUESTION 3: PRINT THE PERCENTAGE OF COURSES IN ENGINEERING                  $no_paint"
echo "$paint$yellow  $no_paint                                                                            $paint$yellow  $no_paint"
echo "$paint$yellow  $no_paint The percentage of courses in engineering is: "$z"%                       $paint$yellow  $no_paint"
echo "$paint$yellow  $no_paint                                                                            $paint$yellow  $no_paint"
echo "$paint$yellow                                                                                $no_paint"

echo -e "\n"
