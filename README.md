# Sri Lankan Cricketers Search Engine 
This repository contains source for a search engine that can used to query Sri Lankan
ODI cricketers. This information retrieval system was build using Elasticsearch and Flask.
This search engine supports both Sinhala and English language queries. The information 
about cricketers were extract from [espncricinfo.com](https://www.espncricinfo.com/player) 
and wikipedia using beautifulsoup.


## Directory Structure

```
├── corpus : scripts realated to data extraction and final corpus
    ├── corpus.json : initial corpus in english language
    ├── corpus_en_to_si_converter.py : convert english text to sinhala using googletrans api
    ├── corpus_preprocessor.py : script to reduce the text field size
    ├── final-corpus.json : final corpus in both english and sinhala languages
    ├── scraper.py : script to exract data espncricinfo.com and wikipedia              
├── objects : player class 
    ├── Player.py : plyaer object class
├── templates : UI related files  
├── app.py : backend of the web app created using Flask
├── create_index.py : script to upload data to Elasticsearch
├── queries.py : script contains all queries
├── search.py : search functions for processing queries and returning results
├── queries.txt :  Example queries supported by search engine  
├── config.py :  ES configuration with host, port, and index name
```

## Data fields

Each cricketer entry contains the following data fields. Biography and Internal Carrier are long text fields.

    1. Full Name ( English and Sinhala )
    2. Birthday 
    3. Batting Style ( English and Sinhala )
    4. Bowling Style ( English and Sinhala )
    5. Role ( English and Sinhala ) 
    6. Education ( English and Sinhala )
    7. Biography ( English and Sinhala )
    8. International Carrier ( English and Sinhala )
    9. Test debut ( English and Sinhala )
    10. ODI debut ( English and Sinhala )
    11. T20 debut ( English and Sinhala )
    12. ODI runs
    13. ODI wickets
    14. Espncricinfo website url

## Data Scraping

The process with scraping data from the site, the HTML/XML parsing library BeautifulSoup was used 
for scraping the web pages.

![Data Scrape Workflow](https://github.com/LakshanWeerasinghe/Sri_Lankan_Cricketer_Search/assets/images/scrape.png)