#handles the parsing of ordinals in text format to the mathematical format
from number_parser import parse

#static class containing functions to obtain equivalent expressions
#Currently:
#Without superfluous spaces, ordinals to mathform, ordinals to textform
class Synonymes(object):
    
   

    #The following dictionaries save the transformations done on a text to obtain "synonyms"


    #Convert ordinal to text (basic dictionary, from 1 to 18) Necessary???
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
    #Convert text to digit

    #Helpermethods

    #Transforms a number (int) to an ordinal number. No testing of it is in the correct range
    def number_to_ordinal_number(n: int):
      if 11 <= (n % 100) <= 13:
        suffix = 'th'
      else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
      return str(n) + suffix
    
            
              
     
     #test all possible variations of a string based on certain conditions (explained in the method)
    @classmethod
    def synonymes(cls,input_s): 
          
         
        results = []
          
          
        #Add the base string
        results.append(input_s)
        
        #Remove useless empty spaces (use that string as the baseline for all further transformations)
        string = (" ").join(input_s.split(" "))
        if(not string == input_s):
           results.append(string)
        
        #Text format (Convert ordinals to text)
        string_text = string
        for key, value in cls.list_of_math_numbers.items():
           string_text = string_text.replace(key, value)
        
        if(not string_text == input_s):
           results.append(string_text)
          
        #Numerical format (Convert text ordinals to numbers)
        
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
           results.append(string_ord)
     
    
        return results

