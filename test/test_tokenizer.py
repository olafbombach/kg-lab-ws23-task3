from source.Tokenizer import Tokenizer



def test_onDict():
   input_dict = {"Conference Title": "2018 26th Euromicro International Conference on Parallel, Distributed and Network-based Processing (PDP)", 
                 "Publisher": "nan", 
                 "Mtg Year":"nan", 
                 "Description":"21-23 March 2018 Location: Cambridge, UK"}
   tok = Tokenizer()
   tok_result = tok.tokenizeProceedings(input_dict)
   print(tok_result)

   assert len(tok_result) > 2  # just a random number
