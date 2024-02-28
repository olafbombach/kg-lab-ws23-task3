# handles the parsing of ordinals in text format to the mathematical format
from number_parser import parse
# Finds dates of the form YYYY-MM-DDDD currently not working
# from dateutil import parser
import calendar
# Open .csv files
import pandas
import json
import openpyxl
# handles parsing of brackets
import re

# dependencies on source code
# TokenSet and Tokens to be used as output for the Tokenizer
from dataclasses import dataclass, field
from typing import Set

#pyparser

from source.pyLookupParser.Tokenizer import *

from source.pyLookupParser.Signature import *

from tqdm import tqdm

@dataclass
class Token:
    """
    One of the outputs of the Tokenizer. Is initialized with the three attributes.
    Post_init later defines a forth attribute called 'token' which is a combination in form of a tuple.
    """
    keyword: str
    category: str
    weight: float

    def __post_init__(self):
        self.token = (self.keyword, self.category, self.weight)


@dataclass
class TokenSet:
    """
    The complete output that is generated by the Tokenizer.
    Initialization is done with no input.
    It can be extended by adding '+' tokens of class Token to it.
    It can further be used as iteration.
    """
    tokens: Set[tuple] = field(default_factory=set)

    def __add__(self, others):
        assert type(others) == Token, "The datatype of other is not chosen correctly."
        self.tokens.add(others.token)
        return TokenSet(tokens=self.tokens)
    
    def __iter__(self):
        return iter(self.tokens)
    
    def len(self):
        return len(self.tokens)

class Tokenizer(object):
    """
    Static class containing functions to obtain equivalent expressions.
    Gives the results as keys in a TokenSet, 
    that also contains a metric for the usefulness of the synonym in the value of the entry
    
    Currently:
    Without superfluous spaces, ordinals to mathform, ordinals to textform
    Uses abbreviation (assumed to be the only expression in brackets or all uppercase)
    Gives out the date of the paper
    Gives out infixes of the title (low scores)
    """


    # The following dictionaries save the transformations done on a text to obtain "synonyms"
    # Convert ordinal to text (basic dictionary, from 1 to 18)
    list_of_math_numbers = {
                         "1st": "First",
                         "2nd": "Second",
                         "3rd": "Third",
                         "4th": "Fourth",
                         "5th": "Fifth",
                         "6th": "Sixth",
                         "7th": "Seventh",
                         "8th": "Eighth",
                         "9th": "Ninth",
                         "10th": "Tenth",
                         "11th": "Eleventh",
                         "12th": "Twelfth",
                         "13th": "Thirdteenth",
                         "14th": "Fourteenth",
                         "15th": "Fifteenth",
                         "16th": "Sixteenth",
                         "17th": "Seventeenth",
                         "18th": "Eighteenth"
                         }
    # Months
    months = dict((month, index) 
                  for index, month in enumerate(calendar.month_abbr) if month)
   
    # Helpermethods

    def is_decimal(string: str) -> bool:
        """
        Checks if a string represents a decimal
        """
        try:
            int(string)
            return True
        except ValueError:
            return False

    def number_to_ordinal_number(n: int) -> str:
        """
        Transforms a number (int) to an ordinal number. 
        No testing of it is in the correct range
        """
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        else:
            suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        return str(n) + suffix

    #Main Methods

    @classmethod
    def synonymes(cls,input_s: str) -> TokenSet: 
        """
        Test all possible variations of a string 
        based on certain conditions (explained in the method).

        Input: String to generate synonymes with
        Output: Dictionary: Keys:Synonymes Values:Scores of the synonymes (How important)
        """
        results = TokenSet()  
          
        # Add the base string score:4
        results = results + Token(input_s, "Base", 100)
        
        # Remove useless empty spaces (use that string as the baseline for all further transformations) score:3
        string = (" ").join(input_s.split(" "))
        if not string == input_s:
            results += Token(string,"Modified",90)
        
        # Text format (Convert ordinals to text), using the dictionary above score:3
        string_text = string
        for key, value in cls.list_of_math_numbers.items():
            string_text = string_text.replace(" "+key, " "+value)
        
        if not string_text == input_s:
            results += Token(string_text, "Modified", 3)
          
        # Numerical format (Convert text ordinals to numbers) score:3
        words = string.split(" ")
        # To be able to change the word list an index is needed
        index = 0
        for word in words:
            if len(word) > 2 and (word[len(word)-2:] == "nd" or word[len(word)-2:] == "st" or word[len(word)-2:] == "th" or word[len(word)-2:] == "rd"):
                old = word
                # Text to number
                new = parse(word)
                # only if parsing was successful change to ordinal
                if not new == old:
                    new = cls.number_to_ordinal_number(int(new))
                    words[index] = new
            index += 1
        string_ord = (" ").join(words)
          
        if not string_ord == input_s:
            results += Token(string_ord, "Modified",3)
           
        # Use Abbreviation (Assumed to be all uppercase, possibly in brackets, and does not start with a number) score:3
        # Numbers (such as years and days of the month are also checked, but with a score of 1)
        words = string.split(" ")

        for word in words:
            uppercase = True
            for i in range(0,len(word)):
                if word[i].islower():
                    uppercase = False
            if len(word) > 0:
                if uppercase:
                    if word[0].isdigit():
                        # year, date ,etc.
                        results += Token(word, "Year", 1)
                    else:
                        # abbreviation (uppercase word)
                        results += Token(word, "Abbreviation",3)
       

        # Abbreviation, this time in brackets (for example (ICIMTech) is not fully uppercase) score:2
        # Checks that the first letter is not a number 
        # Is often eithen an abbreviation, publisher or file type   
        m = re.findall(r"\(([A-Za-z0-9_]+)\)", string)
        for ele in m:
            if not ele[0].isdigit():
                results += Token(ele,"Bracketexpression",2)
       

        # Extract date score:2
        # Search for date of the form YYYY-MM-DD using the datutil parser
        # date = parser.parse(string)
        # if(not (date == None or date == "")):
        #  dateparts = date.split(":")
        # if(len(dateparts) > 2):
        #   date = dateparts[2] + ":" + dateparts[1] + ":" + dateparts[0] #Format DD:MM:YYYY
        #  results[date] = 2
        if False:
            i = 1
        # No date found to parse, determine it assuming the month is a word using the dictionary above
        else: 
            # 0 means nothing found if it stays that way (month, day, year)
            month = 0
            day = 0
            year = 0
            index = 1
        for key, value in cls.months.items():
            if(not string_text.find(key) == -1):
                # There can only be one month
                month = index
            index += 1
            # find year (4 numbers) and day (2 numbers, no more or "-" (f. ex. 22-23 March))
            if not month == 0:
                words = string.split(" ")
                for word in words:
                    # day
                    if len(word) >= 2 and Tokenizer.is_decimal(word[0]) and Tokenizer.is_decimal(word[1]) and (len(word) == 2 or word[2] == "-"):
                        day = int(word[0:2])
                    if len(word) == 4 and Tokenizer.is_decimal(word[0]) and Tokenizer.is_decimal(word[1]) and Tokenizer.is_decimal(word[2]) and Tokenizer.is_decimal(word[3]):
                        year = int(word)
                if not (day == 0 or year == 0):
                    day = str(day)
                    year = str(year)
                    month = str(month)
                    if len(day) == 1:
                        day = "0" + day
                    if len(year) == 1:
                        year = "0" + year
                    if len(month) == 1:
                        month = "0" + month
                    results += Token(day+":"+month+":"+year, "Date", 2)
                    
        #Use pyparser for the analysis (output both a string and the wikidata encoding)
        #Country

        tokenizer2 = TokenizerParser([CountryCategory()])

        item = {"title": input_s}


        token = tokenizer2.tokenize(input_s,item)

        for t in token.getTokenOfCategory("country"):
    
           results += Token(t.value, "Wikidata Identifier", 5)
           
           results += Token(t.tokenStr, "Country", 5) 
      
        #Limit the number of results
        lim = 20

        # Infixes score:1
        for i in range(1, len(words) + 1):
            index = 0
            for word in words:
                if index + i < len(words) + 1:
                    if results.len() < lim:
                       results += Token((" ").join(words[index:index + i]), "Infix",1)
                    else:
                        break
        
        
        return results
    
    def analyzeDesciption(input_s):
        """
        (Not implemented)
        Checks the description in proceedings.com for country, city (not implemented) and date (not implemented) using yLookupParser.
        Input: string representing the description
        Output: List of tokens to add to the tokenset
        """
        results = []        

        #Country

        tokenizer2 = TokenizerParser([CountryCategory()])

        item = {"title": input_s}


        token = tokenizer2.tokenize(input_s,item)

        for t in token.getTokenOfCategory("country"):
    
           results.append (Token(t.value, "Wikidata Identifier", 5))
           
           results.append(Token(t.tokenStr, "Country", 5))
           
        #City

        tokenizer2 = TokenizerParser([CityCategory()])

        item = {"title": input_s}


        token = tokenizer2.tokenize(input_s,item)

        for t in token.getTokenOfCategory("city"):
    
           results.append(Token(t.value, "Wikidata Identifier", 5))
           
           results.append(Token(t.tokenStr, "City", 5))
           

        #Date

        tokenizer2 = TokenizerParser([YearCategory()])

        item = {"title": input_s}


        token = tokenizer2.tokenize(input_s,item)

        for t in token.getTokenOfCategory("year"):
           
           results.append(Token(t.tokenStr, "Year", 5))
           

        
        return results
    
        
        
   
    

    def check_semantics(ts: TokenSet) -> None:
        """
        Check if the token is feasible for the searchengine.
        If the number of parantheses part are unequal, 
        we delete all parantheses of the keyword. 
        """
        ts_new = TokenSet()
        for token in ts:
            if token[0].count("(") != token[0].count(")"):
                new_token = Token(token[0].replace("(", "").replace(")", ""), 
                                  token[1], 
                                  token[2])
                ts_new += new_token
            else:
                ts_new += Token(token[0], token[1], token[2])
        del ts
        
        return ts_new

    @classmethod
    def tokenizeProceedings(cls,dict) -> TokenSet:
        """
        Creates token from the index-th entry in the given pandas dataframe, 
        structured as the proceedings.com excel sheet.
        """
        cols = ['Publisher', 'Conference Title', 'Book Title', 'Series',
                'Description','Mtg Year','Editor','ISBN','Pages','Format',
                'POD Publisher','Publ Year','Subject1','Subject2','Subject3',
                'Subject4','List','Price']
      
        # print(file)
        results = Tokenizer.synonymes(dict['Conference Title'])
        if str(dict['Mtg Year'])[0].isdigit():
            results + Token(str(dict['Mtg Year'])[0:4], "MtgYear",4)
          
        if 'Publisher' in dict and not str(dict['Publisher']) == "nan":
            results += Token(str(dict['Publisher']),"Publisher",2)
            
        if 'Description' in dict and not str(dict['Description']) == "nan":
            tokenList = Tokenizer.analyzeDesciption(dict['Description'])
        
        # checks if semantics with parantheses are correct
        results = cls.check_semantics(results)
        

        
        

        return results

    
    @classmethod
    def initializer(cls,path):
        """
        Dummy for the main class. 
        Loops over all the entries in the database given by path.
        """
        file = pandas.read_excel(path, engine = 'openpyxl')
        results = []
        for i in tqdm(range(0,len(file)-1)):
            dicti = dict()
            dicti["Publisher"] = file.iloc[i]["Publisher"]
            dicti["Mtg Year"] = file.iloc[i]["Mtg Year"]
            dicti["Conference Title"] = file.iloc[i]["Conference Title"]
            dicti["Description"] = file.iloc[i]["Description"]
            print(dicti)
            results.append(Tokenizer.tokenizeProceedings(dicti))
        return results


if __name__ == "__main__":
     Tokenizer.initializer("datasets/proceedings.com/all-nov-23.xlsx")



