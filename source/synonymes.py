#handles the parsing of ordinals in text format to the mathematical format
from number_parser import parse

#Finds dates of the form YYYY-MM-DDDD currently not working
#from dateutil import parser

import calendar


#Open .csv files
import pandas

import json

import openpyxl


#static class containing functions to obtain equivalent expressions
#gives the results as keys in a dictionary, that also contains a metric for the usefulness of the synonym in the value of the entry
#Currently:
#Without superfluous spaces, ordinals to mathform, ordinals to textform
#Uses abbreviation (assumed to be the only expression in brackets or all uppercase)
#Gives out the date of the paper
#Gives out infixes of the title (low scores)
class Tokenizer(object):
    
   

    #The following dictionaries save the transformations done on a text to obtain "synonyms"


    #Convert ordinal to text (basic dictionary, from 1 to 18)
    list_of_math_numbers = {
                         "1st":"First",
                         "2nd":"Second",
                         "3rd":"Third",
                         "4th":"Fourth",
                         "5th":"Fifth",
                         "6th":"Sixth",
                         "7th":"Seventh",
                         "8th":"Eighth",
                         "9th":"Ninth",
                         "10th":"Tenth",
                         "11th":"Eleventh",
                         "12th":"Twelfth",
                         "13th":"Thirdteenth",
                         "14th":"Fourteenth",
                         "15th":"Fifteenth",
                         "16th":"Sixteenth",
                         "17th":"Seventeenth",
                         "18th":"Eighteenth"
              
              }
    #Months

    months = dict((month, index) for index, month in enumerate(calendar.month_abbr) if month)
   

    #Helpermethods

    #checks if a string represents a decimal
    def is_decimal(string):
      try:
        int(string)
        return True
      except ValueError:
        return False

    #Transforms a number (int) to an ordinal number. No testing of it is in the correct range
    def number_to_ordinal_number(n: int):
      if 11 <= (n % 100) <= 13:
        suffix = 'th'
      else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
      return str(n) + suffix
    
            
              
     #Input: String to generate synonymes with
     #Output: Dictionary: Keys:Synonymes Values:Scores of the synonymes (How important)  
     #test all possible variations of a string based on certain conditions (explained in the method)
    @classmethod
    def synonymes(cls,input_s): 
          
         
        results = dict()
          
          
        #Add the base string score:4
        results[input_s] = 100
        
        #Remove useless empty spaces (use that string as the baseline for all further transformations) score:3
        string = (" ").join(input_s.split(" "))
        if(not string == input_s):
           results.append(string+":3")
        
        #Text format (Convert ordinals to text), using the dictionary above score:3
        string_text = string
        for key, value in cls.list_of_math_numbers.items():
           string_text = string_text.replace(" "+key, " "+value)
        
        if(not string_text == input_s):
           results[string_text] = 3
          
        #Numerical format (Convert text ordinals to numbers) score:3
        words = string.split(" ")
        #To be able to change the word list an index is needed
        index = 0
        for word in words:
           if(len(word) > 2 and (word[len(word)-2:] == "nd" or word[len(word)-2:] == "st" or word[len(word)-2:] == "th" or word[len(word)-2:] == "rd")):
              old = word
              #Text to number
              new = parse(word)
              #only if parsing was successful change to ordinal
              if(not new == old):
                  new = cls.number_to_ordinal_number(int(new))
                  words[index] = new
           index += 1
        string_ord = (" ").join(words)
          
        if(not string_ord == input_s):
           results[string_ord] = 3
           
        #Use Abbreviation (Assumed to be all uppercase, possibly in brackets, and does not start with a number) score:3
        #Numbers (such as years and days of the month are also checked, but with a score of 1)
        words = string.split(" ")

        for word in words:
           uppercase = True
           for i in range(0,len(word)):
              if(word[i].islower()):
                 uppercase = False
           if(len(word) > 0):
              if(uppercase):
                 if(word[0].isdigit()):
                     #year, date ,etc.
                     results[word] = 1
                 else:
                     #abbreviation (uppercase word)
                     results[word] = 3
       

        #Abbreviation, this time in brackets (for example (ICIMTech) is not fully uppercase) score:3
        for word in words:
           if(len(word)>2 and word[0] == "(" and word[len(word)-1]==")"):
              results[word[1:len(word)-1]] = 3
       

        #Extract date score:2
        #Search for date of the form YYYY-MM-DD using the datutil parser
        #date = parser.parse(string)
        #if(not (date == None or date == "")):
         #  dateparts = date.split(":")
          # if(len(dateparts) > 2):
           #   date = dateparts[2] + ":" + dateparts[1] + ":" + dateparts[0] #Format DD:MM:YYYY
            #  results[date] = 2
        if(False):
           i = 1
        #No date found to parse, determine it assuming the month is a word using the dictionary above
        else: 
           #0 means nothing found if it stays that way (month, day, year)
           month = 0
           day = 0
           year = 0
           index = 1
        for key, value in cls.months.items():
           if(not string_text.find(key) == -1):
              #There can only be only month
              month = index
           index += 1
           #find year (4 numbers) and day (2 numbers, no more or "-" (f. ex. 22-23 March))
           if(not month == 0):
             words = string.split(" ")
             for word in words:
                #day
                if(len(word) >= 2 and Tokenizer.is_decimal(word[0]) and Tokenizer.is_decimal(word[1]) and (len(word) == 2 or word[2] == "-")):
                   day = int(word[0:2])
                if(len(word) == 4 and Tokenizer.is_decimal(word[0]) and Tokenizer.is_decimal(word[1]) and Tokenizer.is_decimal(word[2]) and Tokenizer.is_decimal(word[3])):
                   year = int(word)
             if(not (day == 0 or year == 0)):
                day = str(day)
                year = str(year)
                month = str(month)
                if(len(day) == 1):
                   day = "0"+day
                if(len(year) == 1):
                   year = "0"+year
                if(len(month) == 1):
                   month = "0"+month
                if(not day+":"+month+":"+year in results):
                   results[day+":"+month+":"+year] = 2
      

        #Infixes score:1

        for i in range(1,len(words)+1):
           index = 0
           for word in words:
             if(not (" ").join(words[index:index + i]) in results and index + i < len(words) + 1):
                results[(" ").join(words[index:index + i])] = 1

        
        #Discard unnecessary Information (end substring at year or end substring at/after Abbreviation)
        return results
    

    #Creates token from the index-th entry in the given pandas dataframe, structured as the .proceedings excel sheet
    @classmethod
    def tokenizeProceedings(cls,file,index):
       
       cols = ['Publisher', 'Conference Title','Book Title','Series','Description','Mtg Year','Editor','ISBN','Pages','Format','POD Publisher','Publ Year','Subject1','Subject2','Subject3','Subject4','List','Price']
       if(index>len(file)):
          raise IndexError("Index must be an integer in the range 0 to "+str(len(file)-1))
      
       #print(file)
       indexCol = file.loc[index]
       results = Tokenizer.synonymes(indexCol['Conference Title'])
       if(str(indexCol['Mtg Year'])[0].isdigit()):
           results[str(indexCol['Mtg Year'])[0:4]] = 4
          
       if(not str(indexCol['Publisher']) == "nan"):
          results[str(indexCol['Publisher'])] = 2
       
       return results

    #Dummy for the main class. Loops over all the entries in the database given by path
    @classmethod
    def initializer(cls,path):
       file = pandas.read_excel(path, engine = 'openpyxl')
       results = []
       for i in range(0,len(file)-1):
          results.append(Tokenizer.tokenizeProceedings(file,i))
        

       return results


