import datetime
import json
from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
from config import *
import random

def parse_str_to_date(datestring):
    # takes datestrings in the format yyyy-mm-dd and returns 
    # corresponding datetime.date object

    year, month, day = map(lambda x: int(x), datestring.split('-'))
    return datetime.date(year, month, day)

def parse_date_to_str(dateobj):
    # takes datetime.date obj and returns string in yyyy-mm-dd format
    return dateobj.strftime("%Y-%m-%d")

def get_week_number(dateobj):
    # takes a date and returns which week of the year contained it (1-52)
    # Week 52 has an 8th day on 12/31
    return int(dateobj.isocalendar()[1])

month_name_to_num = {
    'Jan': 1,
    'Feb': 2,
    'Mar': 3,
    'Apr': 4,
    'May': 5,
    'Jun': 6,
    'Jul': 7,
    'Aug': 8,
    'Sep': 9,
    'Oct': 10,
    'Nov': 11,
    'Dec': 12
}

def parse_table_row(tr_object, year):
    datestring_container = tr_object.find('th')
    name_container = tr_object.find('a')

    datestring = datestring_container.text if datestring_container else ""
    name = name_container.text if name_container else ""

    if datestring and name:
        dateparts = datestring.split(" ")
        date = datetime.date(year, month_name_to_num[dateparts[0]], int(dateparts[1]))
        return Holiday(name, date)

# -------------------------------------------
# Modify the holiday class to 
# 1. Only accept Datetime objects for date.
# 2. You may need to add additional functions
# 3. You may drop the init if you are using @dataclasses
# --------------------------------------------
class Holiday:
      
    def __init__(self,name, date):
        self.name = name
        if isinstance(date, datetime.date):
            self.date = date
        else:
            raise TypeError("date must be a datetime.date object")

    def __str__ (self):
        # String output
        # Holiday output when printed.
        return f"{self.name} ({parse_date_to_str(self.date)})"
    
    def __eq__(self, other):
        return self.name == other.name and self.date == other.date
          
           
# -------------------------------------------
# The HolidayList class acts as a wrapper and container
# For the list of holidays
# Each method has pseudo-code instructions
# --------------------------------------------
class HolidayList:
    def __init__(self):
       self.innerHolidays = []
   
    def addHoliday(self, holidayObj):
        # Make sure holidayObj is an Holiday Object by checking the type
        # Use innerHolidays.append(holidayObj) to add holiday
        # print to the user that you added a holiday
        if isinstance(holidayObj, Holiday):
            self.innerHolidays.append(holidayObj)
            print("\n", holidayObj, " added to list")
        else:
            raise TypeError("Can only add Holiday objects to list of holidays")

    def findHoliday(self, HolidayName, Date):
        # Find Holiday in innerHolidays
        # Return Holiday
        for hday in self.innerHolidays:
            if hday.name == HolidayName and hday.date == parse_str_to_date(Date):
                return hday
        
        print(f"Error:\n{HolidayName} not found")

    def removeHoliday(self, HolidayName, Date):
        # Find Holiday in innerHolidays by searching the name and date combination.
        # remove the Holiday from innerHolidays
        # inform user you deleted the holiday
        hday_to_drop = self.findHoliday(HolidayName, Date)
        if hday_to_drop:
            self.innerHolidays.remove(hday_to_drop)
            print("\n", hday_to_drop, " succesfully removed")


    def read_json(self, filelocation):
        # Read in things from json file location
        # Use addHoliday function to add holidays to inner list.
        with open(filelocation, 'r') as f:
            holiday_dict = json.loads(f.read())
        
        for day in holiday_dict['holidays']:
            self.addHoliday(Holiday(day['name'], parse_str_to_date(day['date'])))
        
    
    def save_to_json(self, filelocation):
        # Write out json file to selected file.
        dump_this_dict = {'holidays': [{'name': hday.name , 'date': parse_date_to_str(hday.date)} for hday in self.innerHolidays]}
        with open(filelocation, 'w') as f:
            f.write(json.dumps(dump_this_dict))
        
    def scrapeHolidays(self):
        # Scrape Holidays from https://www.timeanddate.com/holidays/us/ 
        # Remember, 2 previous years, current year, and 2  years into the future. You can scrape multiple years by adding year to the timeanddate URL. For example https://www.timeanddate.com/holidays/us/2022
        # Check to see if name and date of holiday is in innerHolidays array
        # Add non-duplicates to innerHolidays
        # Handle any exceptions.
        current_year = datetime.date.today().year

        for year in range(current_year-2, current_year+3):
            url = f"{base_timedate_url}{year}"

            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            tbody = soup.find('table', attrs={'id': 'holidays-table'}).find('tbody')

            for row in tbody.find_all('tr'):
                new_hday = parse_table_row(row, year)

                if new_hday and new_hday not in self.innerHolidays:
                    self.addHoliday(new_hday)


    def numHolidays(self):
        # Return the total number of holidays in innerHolidays
        return len(self.innerHolidays)
    
    def filter_holidays_by_week(self, year, week_number):
        # Use a Lambda function to filter by week number and save this as holidays, use the filter on innerHolidays
        # Week number is part of the the Datetime object
        # Cast filter results as list
        # return your holidays

        hdays_in_week = list(filter(lambda hday: hday.date.year == year and get_week_number(hday.date) == week_number, self.innerHolidays))
        return hdays_in_week

    def displayHolidaysInWeek(self, year, week_number):
        # Use your filter_holidays_by_week to get list of holidays within a week as a parameter
        # Output formated holidays in the week. 
        # * Remember to use the holiday __str__ method.

        hdays_to_disp = self.filter_holidays_by_week(year, week_number)
        for hday in hdays_to_disp:
            print(hday)

    def getWeather(self):
        # Convert weekNum to range between two days
        # Use Try / Except to catch problems
        # Query API for weather in that week range
        # Format weather information and return weather string.
        # Use this link: https://openweathermap.org/api
        # API calls not implemented unfortunately, ran out of time

        current_date = datetime.date.today()
        current_year = current_date.year
        current_week_number = get_week_number(current_date)

        hdays_to_disp = self.filter_holidays_by_week(current_year, current_week_number)
        for hday in hdays_to_disp:
            print(hday, f"- {random.choice(test_weather_states)}")


    def viewCurrentWeek(self):
        # Use the Datetime Module to look up current week and year
        # Use your filter_holidays_by_week function to get the list of holidays 
        # for the current week/year
        # Use your displayHolidaysInWeek function to display the holidays in the week
        # Ask user if they want to get the weather
        # If yes, use your getWeather function and display results

        current_date = datetime.date.today()
        current_year = current_date.year
        current_week_number = get_week_number(current_date)

        self.displayHolidaysInWeek(current_year, current_week_number)


def disp_menu():
    # Displays main menu, returns user input
    print(main_menu_text)

    while True:
        selection = input("\nWhat would you like to do? [1-5] ")
        try:
            return int(selection)
        except ValueError:
            print("Invalid selection, please try again")


def stay_in_menu(changes_saved):
    print("Exit\n====")
    if changes_saved:
        choice = input("Are you sure you wish to exit? [y/n]: ")
    else:
        choice = input("Are you sure you wish to exit?\nYour changes will be lost\n[y/n] ")
    
    if choice == 'y':
        print("\nGoodbye!")
        return False
    else:
        return True




def main():
    # Large Pseudo Code steps
    # -------------------------------------
    # 1. Initialize HolidayList Object
    # 2. Load JSON file via HolidayList read_json function
    # 3. Scrape additional holidays using your HolidayList scrapeHolidays function.
    # 3. Create while loop for user to keep adding or working with the Calender
    # 4. Display User Menu (Print the menu)
    # 5. Take user input for their action based on Menu and check the user input for errors
    # 6. Run appropriate method from the HolidayList object depending on what the user input is
    # 7. Ask the User if they would like to Continue, if not, end the while loop, ending the program.  If they do wish to continue, keep the program going. 
    #TODO this

    #Initialize HolidayList object
    hday_list = HolidayList()
    hday_list.read_json('holidays.json')
    hday_list.scrapeHolidays()

    print(f"Holiday Management\n==================")
    print(f"Current size of holiday list {hday_list.numHolidays()}")

    # Display menu and perform user selections
    stay_in_loop = True
    changes_saved = True
    while stay_in_loop:
        selection = disp_menu()
        
        if selection == 1:
            print("\nAdd a Holiday\n=============")
            new_name = input("Holiday: ")
            new_datestring = input("Date: ")
            try:
                new_date = parse_str_to_date(new_datestring)
                hday_list.addHoliday(Holiday(new_name, new_date))
                changes_saved = False
            except ValueError:
                print("Error: \nInvalid date. Please try again")

        elif selection == 2:
            print("\nRemove a Holiday\n================")
            name_2_del = input("Holiday Name: ")
            date_2_del = input("Date: ")
            hday_list.removeHoliday(name_2_del, date_2_del)
            changes_saved = False

        elif selection == 3:
            print("\nSave Holidays List\n==================")
            choice = input("Are you sure you want to save your changes? [y/n]: ")
            if choice == 'n':
                print("Canceled:\nHoliday list file save canceled")
            elif choice == 'y':
                hday_list.save_to_json('new_holiday_list.json')
                print("Success:\nYour changes have been saved")
                changes_saved = True
            else:
                print("Invalid selection, please try again")
        elif selection == 4:
            print("\nView Holidays\n=============")
            which_year = int(input("Which year? "))
            which_week = input("Which week? #[1-52, Leave blank for current week]: ")
            which_week = int(which_week) if which_week else ""
            if which_week:
                hday_list.displayHolidaysInWeek(which_year, which_week)
            else:
                show_weather = input("Would you like to see this week's weather? [y/n]: ")
                if show_weather == 'n':
                    hday_list.viewCurrentWeek()
                else:
                    hday_list.getWeather()

        elif selection == 5:
            stay_in_loop = stay_in_menu(changes_saved)
        else:
            print("Something's gone wrong. Please choose a number between 1 and 5")
        
        if stay_in_loop: input("Press enter ")



if __name__ == "__main__":
    main()



# Additional Hints:
# ---------------------------------------------
# You may need additional helper functions both in and out of the classes, add functions as you need to.
#
# No one function should be more then 50 lines of code, if you need more then 50 lines of code
# excluding comments, break the function into multiple functions.
#
# You can store your raw menu text, and other blocks of texts as raw text files 
# and use placeholder values with the format option.
# Example:
# In the file test.txt is "My name is {fname}, I'm {age}"
# Then you later can read the file into a string "filetxt"
# and substitute the placeholders 
# for example: filetxt.format(fname = "John", age = 36)
# This will make your code far more readable, by seperating text from code.





