from urllib.request import urlopen


from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Progressbar

from re import *


from webbrowser import open as urldisplay


from sqlite3 import *


def download(
    url="http://www.wikipedia.org/",
    target_filename="downloaded_document",
    filename_extension="html",
    save_file=True,
    char_set="UTF-8",
    incognito=False,
):
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
    from urllib.error import URLError

    try:
        if incognito:
            request = Request(url)
            request.add_header(
                "User-Agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                + "AppleWebKit/537.36 (KHTML, like Gecko) "
                + "Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
            )
            print("Warning - Request does not reveal client's true identity.")
            print("          This is both unreliable and unethical!")
            print("          Proceed at your own risk!\n")
        else:
            request = url
        web_page = urlopen(request)
    except ValueError as message:  # probably a syntax error
        print("\nCannot find requested document '" + url + "'")
        print("Error message was:", message, "\n")
        return None
    except HTTPError as message:  # possibly an authorisation problem
        print("\nAccess denied to document at URL '" + url + "'")
        print("Error message was:", message, "\n")
        return None
    except URLError as message:  # probably the wrong server address
        print("\nCannot access web server at URL '" + url + "'")
        print("Error message was:", message, "\n")
        return None
    except Exception as message:  # something entirely unexpected
        print(
            "\nSomething went wrong when trying to download "
            + "the document at URL '"
            + str(url)
            + "'"
        )
        print("Error message was:", message, "\n")
        return None
    try:
        web_page_contents = web_page.read().decode(char_set)
    except UnicodeDecodeError as message:
        print(
            "\nUnable to decode document from URL '"
            + url
            + "' as '"
            + char_set
            + "' characters"
        )
        print("Error message was:", message, "\n")
        return None
    except Exception as message:
        print(
            "\nSomething went wrong when trying to decode "
            + "the document from URL '"
            + url
            + "'"
        )
        print("Error message was:", message, "\n")
        return None
    if save_file:
        try:
            text_file = open(
                target_filename + "." + filename_extension, "w", encoding=char_set
            )
            text_file.write(web_page_contents)
            text_file.close()
        except Exception as message:
            print("\nUnable to write to file '" + target_filename + "'")
            print("Error message was:", message, "\n")
    return web_page_contents


# Create the main window
task_2_main_window = Tk()


# connect to the database
connection = connect("ratings_db.db")
cursor = connection.cursor()


# Your code goes here
# Import datetime module
from datetime import datetime, timedelta


media_urls = [
    "https://www.9now.com.au/live/channel-9",
    "https://www.gamespot.com/new-games/",
    "https://www.eventfinda.com.au/concerts-gig-guide/events/queensland",
]
media_names = [
    "9now.com",
    "gamespot.com",
    "eventfinda.com",
]
media_regex = [
    [
        r'(?<="name":")(.*?)(?=","color)',  # channel
        r'(?<={"title":")(.*?)(?=",)',  # title
        r'(?<=,"startDate":")(.*?)(?=Z",)',  # startDate
        r'(?<=,"endDate":")(.*?)(?=Z",)',  # endDate
    ],
    [
        r'(<h4 class="text-custom-bold".*>)(.*?)(?=<\/h4>)',  # days
        r'(?<=<h3 class="media-title">)(.*?)(?=<\/h3>)',  # titles
    ],
    [
        '(<a href=".*" class="url summary">)(.*?|\n)(?=<\/a>)',  # title
        '(<a .* class="location">)(.*?|\n)(?=<\/span>)',  # location
        r'(?<=<span class="value-title")( .*?)(?=">)',  # time
        '(<span class="category">)(.*?|\n)(?=<\/span>)',  # event type
    ],
]
# setup functions


# Command functions
gamespot_day_indexes = []
gamespot_days = []
# indexes of the content, outside the function definition
# because it needs to be used by other iterations of the function
# with different regex expressions


def process_regex(regex_expression, page_content, selected_media_type):
    return_content = []  # the content that will be returned
    if selected_media_type == 0:
        # 9now.com processing is done differently
        # because the content is in a json format
        for content_index in range(len(page_content) - 1):
            # iterate through the page content
            # the last index is not needed
            # because it is equal to []
            page_content[content_index] = page_content[content_index].replace("\\", "")
            # remove the escape character \ from the json
            return_content.append(
                findall(regex_expression, page_content[content_index])
            )
            # append the regex content to the content list
    elif selected_media_type == 1:
        global gamespot_day_indexes
        # makes the global day_indexes variable accessible
        global gamespot_days
        # makes the global days variable accessible
        temp_content = findall(regex_expression, page_content)
        # gets the regex content from the page content
        # this content will be used to construct the content list
        if regex_expression == r'(?<=<h3 class="media-title">)(.*?)(?=<\/h3>)':
            # this matches to the game titles using regex
            matches = finditer(regex_expression, page_content)
            # returns a match object with all of the match indexes
            match_indexes = []
            # list of indexes of match beginnings
            for match in matches:
                # iterate through the matches
                match_indexes.append(match.start())
                # append the match start index to the list
            day_indexes_iterator = 0
            # iterator for the gamespot_days list
            day_content_list = []
            # list of content to group titles by day
            for content_index in range(len(temp_content)):
                # iterate through the content
                page_content_index = match_indexes[content_index]
                # gets the index of the current content
                # needed to check if the content is in the same day
                if day_indexes_iterator >= len(gamespot_day_indexes) - 1:
                    break
                if page_content_index < gamespot_day_indexes[day_indexes_iterator + 1]:
                    # if the current content index is before the next day index
                    # then the content is in the same day
                    day_content_list.append(
                        [
                            temp_content[content_index],
                            gamespot_days[day_indexes_iterator],
                        ]
                    )
                    # append the content to the temporary list
                else:
                    # the content is outside of the day
                    return_content.append(day_content_list)
                    # append the temporary list to the content list
                    day_indexes_iterator = day_indexes_iterator + 1
                    # increment the iterator to the next day
                    day_content_list = []
                    # reset the day content list
        else:
            gamespot_days_matches = finditer(regex_expression, page_content)
            # get the day indexes match object
            for day_match in gamespot_days_matches:
                # iterate through the matches
                gamespot_day_indexes.append(day_match.end())
                # get the indexes of the days

            for temp_content_days in temp_content:
                gamespot_days.append(temp_content_days[1])
                # get the days from the content

    else:
        return_content = findall(regex_expression, page_content)
        # get the regex content from the page content
        for content_index in range(len(return_content)):
            # iterate through the content
            if isinstance(return_content[content_index], tuple):
                # if the content is a tuple
                # the first and last index of the tuple is not needed
                return_content[content_index] = (
                    return_content[content_index][1]
                    .replace("<.*>", "")
                    .replace("</a>", "")
                    .replace(' title="', "")
                    # removes html tags and attributes
                )
            else:
                # if the content is a string
                return_content[content_index] = (
                    return_content[content_index]
                    .replace("<.*>", "")
                    .replace("</a>", "")
                    .replace(' title="', "")
                )
                # removes html tags and attributes
    return return_content


def process_datetime(content, float_boolean):
    if float_boolean:
        return (
            datetime.strptime(
                content, "%Y-%m-%dT%H:%M:%S.%f"
            )  # convert string to datetime
            + timedelta(hours=10)  # add 10 hours to convert to AEST
        ).ctime()  # convert to string
    else:
        return (
            datetime.strptime(
                content, "%Y-%m-%dT%H:%M:%S"
            )  # convert string to datetime
            + timedelta(hours=10)  # add 10 hours to convert to AEST
        ).ctime()


def process_content(content, selected_media_type):
    if selected_media_type == 0:  # processing data from 9now.com
        return_content = []  # [[channel, title, startDate, endDate], ...]
        for content_index in range(len(content[0])):
            # iterate through
            # each list of titles has a channel so index 0 is used
            # the index content_index is used to iterate through title and time lists
            temp_array = []  # [channel, title, startDate, endDate]
            for content_index_information in range(len(content[1][content_index])):
                # iterate through all the lists of information
                # this iterates through all the shows
                # all shows have a start and an end date
                temp_array.append(
                    [  # creating pairs of shows and the start/end dates
                        content[0][content_index][0],  # channel
                        content[1][content_index][content_index_information],  # title
                        process_datetime(  # process startDate
                            content[2][content_index][content_index_information], True
                        ),
                        process_datetime(  # process startDate
                            content[3][content_index][content_index_information], True
                        ),
                    ]
                )
            return_content.append(temp_array)
            # append the array of shows and dates to the return content
        return return_content  # return the content
    elif selected_media_type == 1:
        # processing data from gamespot.com not needed
        # because the data is already in the correct format
        # when processed in process_regex
        return content
    else:  # processing data from abc.net.au
        return_content = []
        # [[title, time, genre, venue], ...] is the format desired
        # content[0] = titles
        # content[1] = venues
        # content[2] = times
        # content[3] = genres
        for content_index in range(len(content[0])):
            # iterate through the content using titles
            # because each title has a venue and time, but not necessarily a genre
            if content_index > len(content[3]) - 1:
                return_content.append(
                    [
                        content[0][content_index],
                        # append the title to return content
                        process_datetime(
                            content[2][content_index].replace("+10:00", ""), False
                        ),
                        # append the time to return content
                        "",
                        # there is no genre so append an empty string
                        content[1][content_index]
                        # append the venue to return content
                    ]
                )
                # append in the form of [title, time, genre, value]
            else:
                return_content.append(
                    [
                        content[0][content_index],
                        # append the title to return content
                        process_datetime(
                            content[2][content_index].replace("+10:00", ""), False
                        ),
                        # append the time to return content
                        content[3][content_index],
                        # append the genre to return content
                        content[1][content_index]
                        # append the venue to return content
                    ]
                )
                # append in the form of [title, time, genre, value]
        return return_content  # return the content


# method to format the data into a list of strings
def format_data(data):
    result = []
    if isinstance(data, list):  # Check if data is a list
        if all(
            isinstance(item, str) for item in data
        ):  # Check if all list elements are strings
            result.append(
                " ".join(data)
            )  # Join inner list elements into a single string
        else:  # If not all list elements are strings
            for item in data:
                result.extend(format_data(item))  # Recursively process nested lists
    elif isinstance(data, str):
        result.append(data)  # Add string to result
    return result  # Return result


last_selected_media = 0


def get_page_content(event):
    # callback function for the listbox
    listbox_widget = media_list
    # get the listbox widget
    if listbox_widget.curselection() == ():  # if nothing is selected
        return
    selected_media_type = listbox_widget.curselection()[0]
    # get the index of the selected media type

    global last_selected_media
    last_selected_media = selected_media_type

    page_content = download(
        url=media_urls[selected_media_type],
        target_filename=media_names[selected_media_type],
        filename_extension="html",
        save_file=False,
    )
    # download the page content from the url
    # selected media type is used to get the url and filename

    if page_content != None:
        status_label_text.config(
            text="Successfully connected to " + media_names[selected_media_type] + "!"
        )
        # update the status label

        media_content = []
        if selected_media_type == 0:
            # if the selected media is 9now.com
            page_content = findall(r'(?<={\\"signpost\\":)(.*?)(?=\]})', page_content)
            # get the content between the signpost and the end of the json
            # this is the content that contains the channel, title, startDate and endDate

        global gamespot_day_indexes
        global gamespot_days
        # global variable to store the days and their indexes
        gamespot_day_indexes = []
        gamespot_days = []
        # reset the days and their indexes

        for regex in media_regex[selected_media_type]:
            # iterate through the regexes for the selected media type
            media_content.append(
                process_regex(regex, page_content, selected_media_type)
            )
            # process the regex and append the content to media content

        media_content = process_content(media_content, selected_media_type)
        # process the content

        wrapped_content = format_data(media_content)
        # wrap the content in a list

        events_frame_list.delete(0, END)  # Clear the listbox
        for content in wrapped_content:
            # iterate through the content
            events_frame_list.insert(END, content)
            # insert the content into the listbox


def like_media():
    selected_media = (
        events_frame_list.curselection()
    )  # get the index of the selected media

    global last_selected_media  # get the last selected media
    selected_media_type = (
        last_selected_media  # get the index of the selected media type
    )
    cursor.execute(
        "INSERT INTO reviews( media_name, media_type, media_review ) VALUES ( ?, ?, ? ) ",
        (events_frame_list.get(selected_media), media_list.get(selected_media_type), 1),
    )
    # insert the review into the database
    connection.commit()  # commit the changes to the database


def dislike_media():
    selected_media = (
        events_frame_list.curselection()
    )  # get the index of the selected media

    global last_selected_media  # get the last selected media
    selected_media_type = (
        last_selected_media  # get the index of the selected media type
    )
    cursor.execute(
        "INSERT INTO reviews( media_name, media_type, media_review ) VALUES ( ?, ?, ? ) ",
        (events_frame_list.get(selected_media), media_list.get(selected_media_type), 0),
    )
    # insert the review into the database
    connection.commit()  # commit the changes to the database


# Setup the window
window = task_2_main_window

window.title("Neco Arc Media Ratings")
window.geometry("690x560")


# Create the elements
neco_arc_image = PhotoImage(
    file="neco_arc.png"
)  # source: https://typemoon.fandom.com/wiki/Neco-Arc/Remake
neco_arc_label = Label(window, image=neco_arc_image)
neco_arc_label.grid(row=0, column=0, rowspan=25, columnspan=2, padx=10, pady=10)

application_title = Label(window, text="Neco Arc Media Ratings", font="Sergo_UI 20")

status_label = LabelFrame(window, height=50, text="Application Status: ", bg="white")
status_label_text = Label(
    status_label, text="Application is running...", font="Sergo_UI 10", bg="white"
)

media_frame = LabelFrame(window, height=150, text="Select Media Source: ", bg="white")

media_label = Label(media_frame, text="Select Media Source: ")
media_list = Listbox(
    media_frame,
    listvariable=StringVar(value=(["Television", "Video games", "Concerts"])),
    height=3,
    width=61,
)
media_list.bind(
    "<<ListboxSelect>>", get_page_content
)  # bind the listbox to the callback function

events_frame = LabelFrame(
    window, height=150, text="Events Being Reviewed: ", bg="white"
)
events_frame_list = Listbox(
    events_frame,
    height=10,
    width=61,
)


def display_url():
    global last_selected_media
    urldisplay(media_urls[last_selected_media])


media_expand = Button(
    window,
    text="Expand in Browser",
    command=display_url,  # open the url of the selected media type
)

media_like = Button(window, text="Like", command=like_media)  # like the selected media
media_dislike = Button(
    window, text="Dislike", command=dislike_media
)  # dislike the selected media


# Apply the elements to the grid
application_title.grid(row=0, column=2, columnspan=5, rowspan=2, sticky="")

status_label.grid(row=2, column=2, columnspan=5, sticky="we")
status_label_text.grid(row=0, column=0, padx=2, pady=2, columnspan=5)

media_frame.grid(row=3, column=2, pady=(6, 0), columnspan=5, sticky="we")
media_list.grid(row=0, column=0, padx=4, columnspan=5, pady=2, sticky="we")

events_frame.grid(row=5, column=2, columnspan=5, pady=(0, 6), sticky="we")
events_frame_list.grid(row=0, column=0)

media_expand.grid(row=6, column=2, sticky="nw")

media_like.grid(row=7, column=2, pady=1, sticky="w")
media_dislike.grid(row=7, column=2, padx=50, pady=1, sticky="w")


# Start the main loop
task_2_main_window.mainloop()
