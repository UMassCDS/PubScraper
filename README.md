# PubScraper

## Program 1:  TheScraper.py
- Searches PubMed for all publications from a given year for the affiliation “University of Massachusetts Amherst”
- For each hit, it finds the DOI in the citation and saves the citation including title, authors, etc.
- For each hit/DOI, it visits the doi.org site to view the manuscript
- It then scrolls the browser though the manuscript and takes screenshots
- It then stitches the screenshots together and does OCR to convert it to plain text
- It then does this for the remaining papers from that year

## Program 2:  TheSearcher.py
- This takes input from an internal webserver that is “user facing” (currently just a VM on a box in my office).
- It collects submitter name, year to search, and keyword list (this is the critical one and I would offer suggestions for end user input).
- It also accepts a csv file that contains, in my case, 2 columns listing every trainee who was a facility user and their advisor for a timeframe of 2 years from start of search criteria).
- Then it makes matches based on the names-csv->authors in citation and also keywords->raw text.
- I then apply a weighting to the scores and it outputs a ranked list based on probability that includes the entire citation and hyperlink to paper.

# Evaluation scoping notes
## Goals Discussion
### Minimum goal for success:
- Cleaning up and maybe minor modifications to TheScraper code to: 
    - make it slower and thus have a higher hit rate for successful downloads/ocr [VP: more info needed]
    - cron job to have it run on the first of every month to get new papers [VP: easy]
    - emailing me (someone) with the monthly list so that missing articles can be added manually to the db [VP: easy]
- Cleaning up and making an html/php front end for TheSearcher code to: [VP: Do you really want to add the complexity of web hosting? Why a front end instead of just triggering the exact script you'd like run?]
   -  allow manual job submissions for immediate db searching with email delivery [VP: easy, just trigger the same script that the cron job would run, but with user inputs]

### Moon shot success:
- Minimum goal PLUS:
    - Adding other public dbs to TheScraper in order to search instead of just PubMed (i.e. google scholar, etc.) [VP: Complexity around paid API access for Google Scholar, which seems to be fairly closed. There are other databases that may be better options. There's a fair bit of research work here in figuring out how these APIs work and what's available, but the coding itself is straightforward.]
    - Automatically generating a publication list for each of the IALS core facilities on a monthly basis [VP: We need a list of authors to match against. If there's a manually maintained list (e.g. CSV file) with the code or something the code takes as an input parameter, this is fairly easy. Otherwise, if we're interfacing with an external DB, this adds complexity to the system architecture and we'd need to talk about access and maintenance.]
        - This would need input from each core and some mechanism to grab csv files that include names of interest (i.e. users) maybe from CORUM? 
    - Providing a “dashboard” of these stats and ability to drill down into things like topics, departments, etc. from the collected results [VP: more info needed, what are preferred tools?]

### Pain points:
- Time to spend on this – I do not have the time to invest in making even the minimum work well
- Ability – as it is probably obvious, my coding is awful and I have relied a lot of stackexchange and ChatGPT to help solve tiny tasks in my python

### Virginia follow up questions
- Why not use Semantic Scholar's API as opposed to PubMed (difficult to use) or Google Scholar (paid/closed)? We can apply for access and see if it's approved.
- What value are the keywords adding to your analysis. Could we obtain the same value from MeSH keyword terms, summaries, etc...?
- What alternatives did you consider to OCRing the web pages? What about downloading webpage html, PDFs or full-text from APIs? 
- Why do missing articles need to be manually added to the DB? 
- Why do search results need to be delivered by email? Would a web viewer tool be more useful? (I'm thinking Elasticsearch )
- Maintaining an up-to-date list of relevant potential author names (and department information) would be key to getting good results in the search step. If there's already a database (CORUM?) of users, that's great, but that adds complexity of interfacing with the system database. What would be the simplest thing we could do that would work? 
- Who would maintain the code after CDS hands it off? Is there a plan for maintained web-hosting? 


## Scraper notes
1. Read through code for dependency libraries and create a requirements.txt file
    - During this process I noticed these unmaintained dependencies:
        - https://github.com/gijswobben/pymed - archived 2020 and no longer updated. There appears to be a lightly maintained fork at https://github.com/osl-incubator/pymedx and an alterative scraping library https://github.com/jannisborn/paperscraper
        - https://github.com/PyImageSearch/imutils hasn't been updated in 2 years
2. Create a conda environment and install requirements: `conda create -n pubscraper python=3.12`, `pip install -r requirements.txt`
3. Looked into running the code, but there are a lot of local files input files that aren't in git and are undocumented as to their format. Some are just temporary generated files for data processing, but some (especially data.txt) have to come from elsewhere and we need examples: 
```
$ grep -in "open(" *.py
1-TheScraper.py:173:        open(f"text_results/{i}text_output.txt", "w").close()
1-TheScraper.py:177:            file = open(f"text_results/{i}text_output.txt", "a")
1-TheScraper.py:181:        file = open(f"text_results/{i}text_output.txt", "w")
1-TheScraper.py:205:open("annual.txt", "w").close() #this will store all of the manscrupts for each year
1-TheScraper.py:212:with open('data.txt', "r") as f:  #this file should be created from a webform or manually - csv file with needed info (but also some leftover junk that can be pruned)
1-TheScraper.py:224:with open('data.txt', "r") as f:
1-TheScraper.py:247:            with open("annual.txt", "a") as f:
1-TheScraper.py:256:            with open("annual.txt", "a") as f:
1-TheScraper.py:265:        with open("annual.txt", "a") as f:
2-TheSearcher.py:26:    with open(file_name, 'r') as file:
2-TheSearcher.py:43:        with open(file_path, 'r') as file:
2-TheSearcher.py:96:with open(annualsum, 'r') as file:
2-TheSearcher.py:114:with open("tosort_data.csv", 'w') as f:
2-TheSearcher.py:117:with open('tosort_data.csv', 'r') as infile:
2-TheSearcher.py:121:with open('sorted_data.csv', 'w', newline='') as outfile:
2-TheSearcher.py:125:with open("atosort_data.csv", 'w') as f:
2-TheSearcher.py:128:with open('atosort_data.csv', 'r') as infile:
2-TheSearcher.py:132:with open('asorted_data.csv', 'w', newline='') as outfile:
```
4. Made some notes in code or and minor code improvements. 
 - don't need f.close() if you're using the file 'with open(...)` convention
 - Ruff linter suggestions (remove unused imports, bare exceptions)
5. Hard coded dates, affiliation and town and ran the scraper as follows:
```
$ python 1-TheScraper.py 
DATE:  2024-05-01:2024-06-01
AFFL:  University+of+Massachusetts+Amherst
SRCH:  University+of+Massachusetts+Amherst+[ad]+Amherst+[ad]+2024-05-01:2024-06-01+[dp]
FND#:  24
Downloading 1 of 25
GOOD ONE
Transcribing now...
Downloading 2 of 25
SHORTY
Transcribing now...
Downloading 3 of 25
SHORTY
Transcribing now...
Downloading 4 of 25
GOOD ONE
Transcribing now...
Downloading 5 of 25
GOOD ONE
Transcribing now...
Downloading 6 of 25
ERROR Message: no such window: target window already closed
from unknown error: web view not found
  (Session info: chrome=128.0.6613.138)
Stacktrace:
0   chromedriver                        0x0000000100be1208 cxxbridge1$str$ptr + 1927396
1   chromedriver                        0x0000000100bd966c cxxbridge1$str$ptr + 1895752
2   chromedriver                        0x00000001007d4808 cxxbridge1$string$len + 89564
3   chromedriver                        0x00000001007afb0c core::str::slice_error_fail::h6c488016ada29016 + 3776
4   chromedriver                        0x000000010083f4d8 cxxbridge1$string$len + 527020
5   chromedriver                        0x0000000100851c90 cxxbridge1$string$len + 602724
6   chromedriver                        0x000000010080d698 cxxbridge1$string$len + 322668
7   chromedriver                        0x000000010080e310 cxxbridge1$string$len + 325860
8   chromedriver                        0x0000000100ba7e78 cxxbridge1$str$ptr + 1693012
9   chromedriver                        0x0000000100bac77c cxxbridge1$str$ptr + 1711704
10  chromedriver                        0x0000000100b8d3ec cxxbridge1$str$ptr + 1583816
11  chromedriver                        0x0000000100bad04c cxxbridge1$str$ptr + 1713960
12  chromedriver                        0x0000000100b7dfc8 cxxbridge1$str$ptr + 1521316
13  chromedriver                        0x0000000100bcab68 cxxbridge1$str$ptr + 1835588
14  chromedriver                        0x0000000100bcace4 cxxbridge1$str$ptr + 1835968
15  chromedriver                        0x0000000100bd9308 cxxbridge1$str$ptr + 1894884
16  libsystem_pthread.dylib             0x0000000180885f94 _pthread_start + 136
17  libsystem_pthread.dylib             0x0000000180880d34 thread_start + 8

Downloading 7 of 25
GOOD ONE
Transcribing now...
Downloading 8 of 25
GOOD ONE
Transcribing now...
Downloading 9 of 25
GOOD ONE
Transcribing now...
Downloading 10 of 25
ERROR Message: disconnected: not connected to DevTools # I think my computer went to sleep -VP
  (failed to check if window was closed: disconnected: not connected to DevTools)
  (Session info: chrome=128.0.6613.138)
Stacktrace:
0   chromedriver                        0x0000000104b81208 cxxbridge1$str$ptr + 1927396
1   chromedriver                        0x0000000104b7966c cxxbridge1$str$ptr + 1895752
2   chromedriver                        0x0000000104774808 cxxbridge1$string$len + 89564
3   chromedriver                        0x000000010475e658 core::str::slice_error_fail::h6c488016ada29016 + 64012
4   chromedriver                        0x000000010475e598 core::str::slice_error_fail::h6c488016ada29016 + 63820
5   chromedriver                        0x00000001047f1cac cxxbridge1$string$len + 602752
6   chromedriver                        0x00000001047ad698 cxxbridge1$string$len + 322668
7   chromedriver                        0x00000001047ae310 cxxbridge1$string$len + 325860
8   chromedriver                        0x0000000104b47e78 cxxbridge1$str$ptr + 1693012
9   chromedriver                        0x0000000104b4c77c cxxbridge1$str$ptr + 1711704
10  chromedriver                        0x0000000104b2d3ec cxxbridge1$str$ptr + 1583816
11  chromedriver                        0x0000000104b4d04c cxxbridge1$str$ptr + 1713960
12  chromedriver                        0x0000000104b1dfc8 cxxbridge1$str$ptr + 1521316
13  chromedriver                        0x0000000104b6ab68 cxxbridge1$str$ptr + 1835588
14  chromedriver                        0x0000000104b6ace4 cxxbridge1$str$ptr + 1835968
15  chromedriver                        0x0000000104b79308 cxxbridge1$str$ptr + 1894884
16  libsystem_pthread.dylib             0x0000000180885f94 _pthread_start + 136
17  libsystem_pthread.dylib             0x0000000180880d34 thread_start + 8

Downloading 11 of 25
GOOD ONE
Transcribing now...
Downloading 12 of 25
GOOD ONE
Transcribing now...
Downloading 13 of 25
GOOD ONE
Transcribing now...
Downloading 14 of 25
GOOD ONE
Transcribing now...
Downloading 15 of 25
GOOD ONE
Transcribing now...
Downloading 16 of 25
GOOD ONE
Transcribing now...
Downloading 17 of 25
GOOD ONE
Transcribing now...
Downloading 18 of 25
GOOD ONE
Transcribing now...
Downloading 19 of 25
GOOD ONE
Transcribing now...
Downloading 20 of 25
GOOD ONE
Transcribing now...
Downloading 21 of 25
GOOD ONE
Transcribing now...
Downloading 22 of 25
GOOD ONE
Transcribing now...
Downloading 23 of 25
SHORTY
Transcribing now...
Downloading 24 of 25
GOOD ONE
Transcribing now...
```
4. I played around with some different ways of querying the API with the following notes: 
- Tried doing the same query I had used in the script on https://pubmed.ncbi.nlm.nih.gov/advanced/. This is how I noticed the data format I started with was wrong.
- Updated the API query to return a CSV. This is useful and the results match what the web tool returns. Worth noting that article titles sometimes get truncated in the API results, but not in the web results.
- You can run searches on the command line with https://www.ncbi.nlm.nih.gov/books/NBK179288/ like `$ esearch -db pubmed -query "University of Massachusetts Amherst[AFFL]" -mindate "2024/05/01" -maxdate "2024/06/01"`, which is good for testing number of results.

## Searcher Notes
I didn't try running this, because I don't have files to reference potential author names. Looking through the file, there are some efficiency improvements around sorting and I have some questions on the scoring. 


## Questions
- Why use Selenium -> screenshot -> OCR, rather than text retrieval from the PubMed APIs?
- What dashboard or data browsing tools are the end-users most comfortable with? (CSV, Excel, SQL? what about Elasticsearch or Tableau?) Did you consider using a database (SQL) or search index system (Elasticsearch)? Why or why not?  
- Did you run into any challenges or limitations with using the PubMed APIs? (Some of their guidelines seem fairly restrictive, see https://www.ncbi.nlm.nih.gov/pmc/tools/oai/)
- Why is the data.txt input to the TheScraper.py generated manually? What did does it contain and how does that data contribute to the rest of the scraper's behaviour? Why does the code read the whole file but only use the last line for creating the query?
- How certain are we about the search query formulation? Is it getting the results that you want? What is "town" providing in the search query string? Actually trying out the query on https://pubmed.ncbi.nlm.nih.gov/advanced/ would be helpful. 
    -  You can use the advanced search options on https://pubmed.ncbi.nlm.nih.gov/advanced/ to build queries. For example, search for "Affiliation=University of Massachusetts Amherst" With a publication date of 6/1/2023-6/1/2024 gives `https://pubmed.ncbi.nlm.nih.gov/?term=%28%28%222023%2F06%2F01%22%5BDate+-+Publication%5D+%3A+%222024%2F06%2F01%22%5BDate+-+Publication%5D%29%29+AND+%28University+of+Massachusetts+Amherst%5BAffiliation%5D%29&sort=`. This is useful for testing, especially since the API isn't well documented. You can use a tool like https://text.makeup to decode the URL string to be more readable and the python urlparse library to encode. 
    - Note that by changing the existing search to `f'(("{startdate}":"{enddate}"[dp])AND(University+of+Massachusetts+Amherst[ad]))'` I get the same number of results as the original search query with town.
- What's the importance of obtaining the full text? Scraping screenshots to OCR seems more unreliable than trying to grab full text via HTML or even PDFs directly from PubMed when available. Many publishers (Wiley) are using the "Verify you are human" checkboxes or other pop ups that block scrapers.
- Keyword counting: 
    - Since you're using the string.count(keyword) method for counting the number of times a term appears in a document, you'll count terms even when they're sub-parts of another word (e.g. "cat" will be counted even if only the word "category" appears in text). Do you want full word matches or is this potential inaccuracy okay? 
    - Why take a specific set of keywords as input? What happens if you want to add a new keyword later?
    - Key terms: Why not use the [MeSH](https://www.nlm.nih.gov/mesh/meshhome.html) terms from each PubMed paper? 
- Keyword scoring: 
    - Why multiply by 100? 


## TODO
- [ ] Python packaging best practices: dependency lists, installation instructions
- [ ] Get examples of the data.txt input file. What formats do input data need to be in? 
- [ ] Standardize data formats (use well-formed CSV, JSON, data structures, rather than ad-hoc text files)
- [ ] Data pipeline documentation
- [ ] Automate data pipelines to run on a schedule or prompted by user input
- [ ] Use headless browser option in Selenium so that you can use your computer while this thing is running
- [ ] Speed up processing code using pandas (and maybe dask) to work with dataframes (up-sides: multiprocessing, computational efficiency, more checks on data formatting, standardized CSV formats, downsides: future maintainers will need to know pandas)


# References 
- https://www.ncbi.nlm.nih.gov/books/NBK25499/
- Handy command line tool for testing queries https://www.ncbi.nlm.nih.gov/books/NBK179288/
- Expert search tips from Johns Hopkins https://browse.welch.jhmi.edu/searching/pubmed-search-tips
- PubMed format tags are at the very bottom https://pubmed.ncbi.nlm.nih.gov/help/#automatic-term-mapping