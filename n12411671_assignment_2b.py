#-----Statement of Authorship----------------------------------------#
#
# This is an individual assessment task for QUT's teaching unit
# IFB104, "Building IT Systems". By submitting
# this code I agree that it represents my own work. I am aware of
# the University rule that a student must not act in a manner
# which constitutes academic dishonesty as stated and explained
# in QUT's Manual of Policies and Procedures, Section C/5.3
# "Academic Integrity" and Section E/2.1 "Student Code of Conduct".
#
# Put your student number here as an integer and your name as a
# character string:
#
student_number = 12411671
student_name = "Hayden Jenner"
#
# NB: All files submitted for this assessable task will be subjected
# to automated plagiarism analysis using a tool such as the Measure
# of Software Similarity (http://theory.stanford.edu/~aiken/moss/).
#
#--------------------------------------------------------------------#


#-----Assessment Task 2 Description----------------------------------#
#
#  In this assessment you will combine your knowledge of Python
#  programming, and Graphical User Interface design to produce
#  a robust, interactive "app" that allows user to view 
#  data from a data source.
#
#  See the client's briefings accompanying this file for full
#  details.
#
#  Note that this assessable assignment is in multiple parts,
#  simulating incremental release of instructions by a paying
#  "client".  This single template file will be used for all parts,
#  together with some non-Python support files.
#
#--------------------------------------------------------------------#

#-----Set up---------------------------------------------------------#

# This section imports standard Python 3 modules sufficient to
# complete this assignment.  Don't change any of the code in this
# section, but you are free to import other Python 3 modules
# to support your solution, provided they are standard ones that
# are already supplied by default as part of a normal Python/IDLE
# installation.
#
# However, you may NOT use any Python modules that need to be
# downloaded and installed separately, such as "Beautiful Soup" or
# "Pillow", because the markers will not have access to such modules
# and will not be able to run your code.  Only modules that are part
# of a standard Python 3 installation may be used.

# A function for exiting the program immediately (renamed
# because "exit" is already a standard Python function).
from sys import exit as abort

# Some standard Tkinter functions.  [You WILL need to use
# SOME of these functions in your solution.]  You may also
# import other widgets from the "tkinter" module, provided they
# are standard ones and don't need to be downloaded and installed
# separately.  (NB: Although you can import individual widgets
# from the "tkinter.tkk" module, DON'T import ALL of them
# using a "*" wildcard because the "tkinter.tkk" module
# includes alternative versions of standard widgets
# like "Label" which leads to confusion.  If you want to use
# a widget from the tkinter.ttk module name it explicitly,
# as is done below for the progress bar widget.)
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Progressbar

# Functions for finding occurrences of a pattern defined
# via a regular expression.  [You do not necessarily need to
# use these functions in your solution, because the problem
# may be solvable with the string "find" function, but it will
# be difficult to produce a concise and robust solution
# without using regular expressions.]
from re import *

# All the standard SQLite database functions.  [You WILL need
# to use some of these in your solution.]
from sqlite3 import *


#-----Validity Check-------------------------------------------------#
#
# This section confirms that the student has declared their
# authorship.  You must NOT change any of the code below.
#

if not isinstance(student_number, int):
    print('\nUnable to run: No student number supplied',
          '(must be an integer)\n')
    abort()
if not isinstance(student_name, str):
    print('\nUnable to run: No student name supplied',
          '(must be a character string)\n')
    abort()
#--------------------------------------------------------------------#
# Connection to database
connection = connect(database = 'movies.db')

# Create cursor
movies_db = connection.cursor()

# Main window configuration
main_window = Tk()
main_window.title("MoviVision Media Movie Search")
main_window.geometry("500x700")    

main_window.minsize(width=500, height=700)
main_window.iconbitmap("images/logoicon.ico")
main_window.configure(bg="skyblue")
#-----Student's Solution---------------------------------------------#
# Put your solution below.
# Movies raw data definition
raw_data = movies_db.execute("SELECT * FROM movies").fetchall()
# As a starting point, you should consider defining functions for:
# - Cleaning Text
# Replace HTML elements list
html_elements = {"&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"', "&#39;": "'", "&nbsp;": " "}
def clean_text(input_data): # input is an tuple inside an array
    full_cleaned_list = [] # define list to fill with fully cleaned output
    for each_film in input_data: # loop through each tuple
        cleaned_data = [] # list for html elements removed
        for each_film_detail in each_film: # loop through each film detail entry
            no_html = sub(r"<(.*?)>", "", str(each_film_detail)) # remove everything within < and > (html elements)
            for elements_present in findall(r"&.[^ ]*?;", no_html): # find prescence of character codes
                no_html = (sub(r"&.[^ ]*?;", html_elements[elements_present], no_html)) # substitute html character codes
            cleaned_data.append(no_html) # append new cleaned detail
        full_cleaned_list.append(cleaned_data) # makes data a list within a list ([[][][]])
    return full_cleaned_list # output is cleaned version of input in a list

cleaned_movie_list = clean_text(raw_data) # define list to call instead of running clean_text repeatedly

# Defining initial current film list
current_film_list = cleaned_movie_list
search_master_dictionary = [] # contains all dictionary entries of films present in search
for each in cleaned_movie_list:
    search_fields = {} # individual dictionary entry
    search_fields ["movie_id"] = each[0]
    search_fields ["title"] = each[1]
    search_fields ["synopsis"] = each[2]
    movies_db.execute("SELECT full_name FROM directors WHERE director_id IN (SELECT director_id FROM direction WHERE movie_id ="+each[0]+")")
    director = movies_db.fetchone()
    search_fields ["director"] = director[0]
    movies_db.execute("SELECT full_name FROM actors WHERE actor_id IN (SELECT actor_id FROM castings WHERE movie_id ="+each[0]+")")
    actor = movies_db.fetchone()
    search_fields ["actor"] = actor[0]
    search_master_dictionary.append(search_fields)
# - Searching Movies
def search_movie():
    global current_film_list
    current_film_list=[] # Clear current film list
    # Get search
    search = search_bar.get()
    for search_field in search_master_dictionary: # search through each search field (title, synopsis, director, actor)
        if search.lower() in ' '.join(search_field.values()).lower(): # if search present in field (i.e. title matches)
            current_film_list.append(cleaned_movie_list[int(search_field["movie_id"])-1]) # append movie (using master cleaned list) to current_film_list
    # Update film title list with search relevant items
    update()
    # Above listbox, show search result number and clear search button
    if search == '':
        search_results.grid_forget()
        clear_search_button.grid_forget()
    else:
        if len(current_film_list) > 0: # if there are any results
            search_results.config(text="'"+search_bar.get()+"' returned "+str(len(current_film_list))+" result/s")
        else: # if there arent any results
            search_results.config(text="No results found for '"+search_bar.get()+"'") # return number of results
        search_results.grid(row=3, column=0, sticky=EW, pady=2, columnspan=2)
        clear_search_button.grid(row=3, column=2, sticky=N)


# Clear search
def clear():
    search_bar.delete(0,END)
    search_movie()

# - Displaying Movie Details
def display_placeholder(event): # display while film is selected, but details tab isn't
    selection = film_titles.curselection() # get film title that is selected
    film_details.delete(1.0,END) # delete everything in the list box
    if selection != ():
        film_details.configure(state=NORMAL) # re-enable editing of list box
        film_details.delete(1.0,END) # delete everything in the list box
        film_details.insert(END, current_film_list[selection[0]][1], "film_title")
        film_details.insert(END, "\nClick above tabs for film information")
        film_details.configure(state=DISABLED) # disable editing

# Movie description
def display_description():
    selection = film_titles.curselection() # get film title that is selected
    if selection != ():
        film_details.configure(state=NORMAL) # re-enable editing of list box
        film_details.delete(1.0,END) # delete everything in list box
        film_details.insert(END, current_film_list[selection[0]][1] + "\n", "film_title") # Insert details about film - selection[0] = index value of film in current_film_list
        film_details.insert(END, current_film_list[selection[0]][2])
        film_details.configure(state=DISABLED)  # disable editing

# Movie details
def display_details():
    selection = film_titles.curselection() # get film title that is selected
    if selection != ():
        film_details.configure(state=NORMAL) # re-enable editing of list box
        film_details.delete(1.0,END) # delete everything in list box
        film_details.insert(END, current_film_list[selection[0]][1] + "\n", "film_title") # Insert details about film - selection[0] = index value of film in current_film_list
        film_details.insert(END, "Release year - " + current_film_list[selection[0]][3] + "\n")
        film_details.insert(END, "Length - " + current_film_list[selection[0]][4] + " minutes \n")
        film_details.insert(END, "MPAA Rating - " + current_film_list[selection[0]][5] + "\n")
        film_details.insert(END, "Country - " + current_film_list[selection[0]][6])
        film_details.configure(state=DISABLED)  # disable editing

# Movie credits
def display_credits():
    selection = film_titles.curselection() # get film title that is selected
    if selection != ():
        film_details.configure(state=NORMAL) # re-enable editing of list box
        film_details.delete(1.0,END) # delete everything in list box
        film_details.insert(END, current_film_list[selection[0]][1] + "\n", "film_title") # Insert details about film - selection[0] = index value of film in current_film_list
        movies_db.execute("SELECT directors.full_name FROM direction INNER JOIN directors on direction.director_id=directors.director_id WHERE direction.movie_id="+current_film_list[selection[0]][0]+"") # search db for director
        director = movies_db.fetchone() # director database result as tuple ('director_name')
        film_details.insert(END, "Director - " + director[0] + "\n")
        movies_db.execute("SELECT actors.full_name FROM castings INNER JOIN actors on castings.actor_id=actors.actor_id WHERE castings.movie_id="+current_film_list[selection[0]][0]+"") # search db for lead actor
        lead_actor = movies_db.fetchone() # actor database result as tuple
        film_details.insert(END, "Lead actor - " + lead_actor[0] + "\n")
        movies_db.execute("SELECT actors.birth_year FROM castings INNER JOIN actors on castings.actor_id=actors.actor_id WHERE castings.movie_id="+current_film_list[selection[0]][0]+"")
        actor_birth_year = movies_db.fetchone()
        film_details.insert(END, "Lead actor birth year - " + str(actor_birth_year[0]) + "\n")
        movies_db.execute("SELECT actors.nationality FROM castings INNER JOIN actors on castings.actor_id=actors.actor_id WHERE castings.movie_id="+current_film_list[selection[0]][0]+"")
        actor_nationality = movies_db.fetchone()
        film_details.insert(END, "Lead actor nationality - " + actor_nationality[0])
        film_details.configure(state=DISABLED)  # disable editing
# - Interface Setup for Application Branding
# - Interface Setup for Search Input
# - Interface Setup for Status Label(s)
# - Interface Setup for the Search Results area
# - Interface Setup for the Movie Details area

def update():
    film_titles.delete(0, END) # Deletes all entries in listbox
    # Add new entries
    for film in current_film_list:
        film_titles.insert(END, film[1])

# Grid configuring
main_frame = Frame(main_window, bg="skyblue") # main_frame contains the whole window - helps with adjusting widgets with different window sizes
main_frame.grid(row=0, column=0, sticky="NESW") # configure whole grid
main_frame.grid_rowconfigure(0, weight=1) # weight=1 enables column width adjustment
main_frame.grid_columnconfigure([0,1,2], weight=1) # 3 columns (used for movie details tabs)

# Define search query features, so that they can dynamicaly dissapear upon certain conditions
clear_search_button = Button(main_frame, text="Clear Search", command=lambda: clear(), cursor="hand2")
search_results = Label(main_frame, text="", bg="skyblue")
# Window title/label
title_frame=Frame(main_frame, bg="skyblue")

# Logo
img = PhotoImage(file="images/tinylogo.png")
logo = Label(title_frame, image=img, bg="skyblue")
logo.grid(row=0, column=0, sticky=EW, pady=2)

# Title text
movivision_title = Label(title_frame, text="MoviVision Media", font=("Arial", 25), bg="skyblue")
movivision_title.grid(row=0, column=1, sticky=EW, pady=2)

title_frame.grid(row=0, column=0, sticky=N, pady=2, columnspan=3)

# Search bar
search_bar_label = Label(main_frame, text="Enter search here...", pady=2, bg="skyblue")
search_bar_label.grid(row=1, column=0, sticky=EW, pady=2, columnspan=3)

search_bar = Entry(main_frame)
search_bar.focus_set()
search_bar.grid(row=2, column=0, sticky=EW, pady=3, columnspan=2)
#search_bar.bind("<KeyRelease>", search_movie)
search_button = Button(main_frame, text="Search", command=search_movie, cursor="hand2")
search_button.grid(row=2, column=2, sticky=EW, pady=3, padx=5)

# Frame to contain scroll bar and film titles list
film_list_frame = Frame(main_frame, pady=20)
film_scroll = Scrollbar(film_list_frame, orient=VERTICAL)

# Film title full listbox
film_titles = Listbox(film_list_frame, width=50, height=10, justify=CENTER, yscrollcommand=film_scroll.set, cursor="hand2")
update() # update list to show search results
# configuring scrollbar behaviour
film_scroll.config(command=film_titles.yview)
film_scroll.pack(side=RIGHT, fill=Y)
film_list_frame.grid(row=4, column=0, sticky=EW, pady=3, columnspan=3)
film_titles.pack()
film_titles.bind("<<ListboxSelect>>", display_placeholder)

# Field for showing film details
film_description_tab = Button(main_frame, command=display_description, text="Description/Synopsis", pady=2, bg="skyblue")
film_description_tab.grid(row=5, column=0, sticky=EW, pady=2)

film_details_tab = Button(main_frame, command=display_details, text="Details", pady=2, bg="skyblue")
film_details_tab.grid(row=5, column=1, sticky=EW, pady=2)

film_credits_tab = Button(main_frame, command=display_credits, text="Credits", pady=2, bg="skyblue")
film_credits_tab.grid(row=5, column=2, sticky=EW, pady=2)

film_details = Text(main_frame, state=DISABLED, padx=10, wrap=WORD, spacing1=5, spacing3=5, width=50, height=10)
film_details.grid(row=6, column=0, sticky=N, pady=3, columnspan=3)
film_details.configure(state=NORMAL)
film_details.insert(END, "No film selected")
film_details.configure(state=DISABLED)
film_details.tag_configure("film_title", justify="center", font="bold")


main_frame.pack(fill="both")
main_window.mainloop()