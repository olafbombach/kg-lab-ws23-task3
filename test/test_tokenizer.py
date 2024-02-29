from source.Tokenizer import *



def test_onDict():
   assert Tokenizer.tokenizeProceedings({"Conference Title": "2018 26th Euromicro International Conference on Parallel, Distributed and Network-based Processing (PDP)", "Publisher": "nan", "Mtg Year":"nan", "Description":"21-23 March 2018 Location: Cambridge, UK"}).equals(TokenSet()+Token('2018', 'Year', 4)+Token('2018 26th Euromicro International Conference on Parallel, Distributed and Network-based Processing', 'Infix', 1) + Token('2018 26th Euromicro International Conference on', 'Infix', 1) + Token('(PDP)', 'Acronym', 2) + Token('2018 26th Euromicro', 'Infix', 1) + Token('2018 26th Euromicro International Conference on Parallel, Distributed and Network-based Processing (PDP)', 'Base', 100) + Token('2018 26th Euromicro International', 'Infix', 1) + Token('2018 26th Euromicro International Conference on Parallel,', 'Infix', 1) + Token('2018 26th Euromicro International Conference on Parallel, Distributed and', 'Infix', 1) + Token('2018', 'Infix', 1) + Token('2018 26th Euromicro International Conference on Parallel, Distributed and Network-based', 'Infix', 1) + Token('PDP', 'Acronym', 2) + Token('2018 26th', 'Infix', 1) + Token('2018 26th Euromicro International Conference on Parallel, Distributed', 'Infix', 1) + Token('2018 26th Euromicro International Conference on Parallel, Distributed and Network-based Processing (PDP)', 'Infix', 1) + Token('2018 26th Euromicro International Conference', 'Infix', 1))
