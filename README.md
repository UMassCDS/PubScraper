# PubScraper

Program 1:  TheScraper.py

-Searches PubMed for all publications from a given year for the affiliation “University of Massachusetts Amherst”

-For each hit, it finds the DOI in the citation and saves the citation including title, authors, etc.

-For each hit/DOI, it visits the doi.org site to view the manuscript

-It then scrolls the browser though the manuscript and takes screenshots

-It then stitches the screenshots together and does OCR to convert it to plain text

-It then does this for the remaining papers from that year
 


Program 2:  TheSearcher.py

-This takes input from an internal webserver that is “user facing” (currently just a VM on a box in my office).

-It collects submitter name, year to search, and keyword list (this is the critical one and I would offer suggestions for 
end user input).

-It also accepts a csv file that contains, in my case, 2 columns listing every trainee who was a facility user and their advisor for a timeframe of 2 years from start of search criteria).

-Then it makes matches based on the names-csv->authors in citation and also keywords->raw text.

-I then apply a weighting to the scores and it outputs a ranked list based on probability that includes the entire citation and hyperlink to paper.

# Evaluation scoping notes
## Development notes
1. Read through code for dependency libraries and create a requirements.txt file
    - During this process I noticed these unmaintained dependencies:
        - https://github.com/gijswobben/pymed - archived 2020 and no longer updated. There appears to be a lightly maintained fork at https://github.com/osl-incubator/pymedx 
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


## Questions
- Why use Selenium -> screenshot -> OCR, rather than text retrieval from the PubMed APIs?
- Did you consider using a database (SQL) or search index system (Elasticsearch)? 
- Did you run into any challenges or limitations with using the PubMed APIs? (Some of their guidelines seem fairly restrictive, see https://www.ncbi.nlm.nih.gov/pmc/tools/oai/)
- Why is the data.txt input to the TheScraper.py generated manually? What did does it contain and how does that data contribute to the rest of the scraper's behaviour?

## TODO
- [ ] Python packaging best practices: dependency lists, installation instructions
- [ ] Get examples of the data.txt input file
- [ ] Standardize data formats (use well-formed CSV, JSON, data structures, rather than ad-hoc text files)
- [ ] Data pipeline documentation
- [ ] Automate data pipelines to run on a schedule or prompted by user input


