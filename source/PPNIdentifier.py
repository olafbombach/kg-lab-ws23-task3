import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import polars as pl

def ppnidentifier(isbn, output_type_k10plus=False):
    """
    returns (PPN or k10plus URL: String, record found: bool, PPN found: bool)
    """
    #query tib with sru
    SRU_query_prefix="https://www.tib.eu/sru/tibkat?"
    #since we assume a full isbn is given, this query type is sufficient
    query_type="query="
    url=SRU_query_prefix+query_type+isbn
    page = urlopen(url)
    xml_file = page.read().decode("utf-8")
    soup = BeautifulSoup(xml_file, "xml")
    records=soup.find_all('numberOfRecords')
    if len(records)>0:
        if records[0].string=="0":
            return (None, False, False)
    identifier=soup.find_all('dc:identifier')
    if len(identifier)>0:
        ppn = identifier[0].string.replace("TIBKAT:", "")
    else:
        return (None, True, False)
    if output_type_k10plus:
        k10plus_prefix="https://opac.k10plus.de/DB=2.299/CMD?ACT=SRCHA&IKT=1016&TRM=$"
        return (k10plus_prefix+ppn, True, True)
    else:
        return (ppn, True, True)
    
def iter_ppnidentifier(isbns, output_type_k10plus=False):
    f = open("ISBNtoPPN.csv", "w")
    f.write("ISBN;PPN;foundinTIB;PPNfound\n")
    isbns=isbns.filter(pl.col("ISBN") != "")
    datalength=isbns.shape[0]
    DataProcessed=0
    print("Begin processing "+ str(datalength)+ " items")
    resume=False
    for isbn in isbns.iter_rows():
        if isbn[0]!="9781604238631" and not resume:
            DataProcessed+=1
            if DataProcessed%1000==0:
                print(str(DataProcessed) +"out of"+ str(datalength) +"items processed")
            continue
        resume=True
        ppn, foundinTIB, PPNfound=ppnidentifier(isbn[0])
        f.write(isbn[0]+";"+str(ppn)+";"+str(foundinTIB)+";"+str(PPNfound)+"\n")
        DataProcessed+=1
        if DataProcessed%1000==0:
            print(str(DataProcessed) +"out of"+ str(datalength) +"items processed")
    f.close()
    print(str(DataProcessed) +" out of "+ str(datalength) +" items processed")
    return

