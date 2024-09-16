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
- What alternatives did you consider to OCRing the web pages? What about downloading PDFs or full-text from APIs? 
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

 ## Additional observations
 - You can use the advanced search options on https://pubmed.ncbi.nlm.nih.gov/advanced/ to build queries. For example, search for "Affiliation=University of Massachusetts Amherst" With a publication date of 6/1/2023-6/1/2024 gives `https://pubmed.ncbi.nlm.nih.gov/?term=%28%28%222023%2F06%2F01%22%5BDate+-+Publication%5D+%3A+%222024%2F06%2F01%22%5BDate+-+Publication%5D%29%29+AND+%28University+of+Massachusetts+Amherst%5BAffiliation%5D%29&sort=`. This is useful for testing, especially since the API isn't well documented. You can use a tool like https://text.makeup to decode the URL string to be more readable and the python urlparse library to encode. 


## Questions
- Why use Selenium -> screenshot -> OCR, rather than text retrieval from the PubMed APIs?
- What dashboard or data browsing tools are the end-users most comfortable with? (CSV, Excel, SQL? what about Elasticsearch or Tableau?) Did you consider using a database (SQL) or search index system (Elasticsearch)? Why or why not?  
- Did you run into any challenges or limitations with using the PubMed APIs? (Some of their guidelines seem fairly restrictive, see https://www.ncbi.nlm.nih.gov/pmc/tools/oai/)
- Why is the data.txt input to the TheScraper.py generated manually? What did does it contain and how does that data contribute to the rest of the scraper's behaviour? Why does the code read the whole file but only use the last line for creating the query?
- How certain are we about the search query formulation? Is it getting the results that you want? What is "town" providing in the search query string? Actually trying out the query on https://pubmed.ncbi.nlm.nih.gov/advanced/ would be helpful. 
- Key terms: Why not use the [MeSH](https://www.nlm.nih.gov/mesh/meshhome.html) terms from each PubMed paper? 


## TODO
- [ ] Python packaging best practices: dependency lists, installation instructions
- [ ] Get examples of the data.txt input file. What formats do input data need to be in? 
- [ ] Standardize data formats (use well-formed CSV, JSON, data structures, rather than ad-hoc text files)
- [ ] Data pipeline documentation
- [ ] Automate data pipelines to run on a schedule or prompted by user input


