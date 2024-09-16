# This code is intended to run slowly, maybe via a cron job every month or so to grab new publications
#
# This code takes in a search year from input (or other) and then finds all manuscripts on PubMed that
# match the affiliation (for instance, University of Massachusetts).  It then attempts to "read"
# each manuscript and create a plain text file containing the contents for use in TheSearcher code.
#
# Outputs are a file with article number (internally generated), judgement of quality, and citation
#
##########
##  To do
##  1) create year directory
##  2) catch all citations with authors and all PMID stuff into a file or text files
##  3) download and OCR all that it can

import math
import os
import random
import re
import shutil
import tempfile
import time

import cv2
import imutils
import pandas as pd
from pymed import PubMed
from pytesseract import pytesseract
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from skimage.metrics import structural_similarity


# main search tool that makes use of the pymed library and the PubMed API
def search(search_term, max_result):
    pubmed = PubMed(tool="PubMedSearcher", email="chamb1@gmail.com")
    results = pubmed.query(search_term, max_results=max_result)
    articleList = []
    articleInfo = {}
    article_records = []
    for article in results:
        articleDict = article.toDict()
        article_records.append(articleDict)
        if articleDict["doi"] is None:
            continue
        articleList.append(articleDict)
        articleInfo[articleDict["doi"].split("\n")[0]] = articleDict
    print("FND#: ", len(articleList))
    pubmedDOI_list = []
    for paper in articleList:
        currentDOI = paper["doi"].split("\n")[0]
        pubmedDOI_list.append(currentDOI)
    articles_df = pd.DataFrame.from_records(article_records)
    return articleInfo, pubmedDOI_list, len(pubmedDOI_list), articles_df


# use selenium to visit doi.org website and grab snapshots as bot scrolls through manuscript
def download(doi, name):
    """Visit webpage at DOI, then scroll through the whole webpage, taking screenshots of each window.
    Finally stich all screenshots together in a single image and save to the `name` filepath

    Args:
        doi (str): Webpage to scrape text from via screenshots
        name (str): Path where final image will be saved

    Returns:
        None
    """
    slpt1 = random.randrange(1, 5)
    slpt2 = random.randrange(2, 4)

    if not os.path.exists("screenshots"):
        os.mkdir("screenshots")
    chrome_options = Options()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-popup-blocking")  # Disable popup blocking
    chrome_options.add_argument("--disable-notifications")  # Disable notifications
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_prefs = {"profile.default_content_settings.cookies": 1}
    chrome_options.add_experimental_option("prefs", chrome_prefs)
    chrome_options.add_argument("--remote-debugging-port=9222")
    temp_user_data_dir = tempfile.mkdtemp()
    chrome_options.add_argument(f"--user-data-dir={temp_user_data_dir}")
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    driver.get(f"https://doi.org/{doi}")
    time.sleep(slpt1)
    accept_button_xpath = "//button[contains(text(), 'Accept') or contains(text(), 'I Accept') or contains(text(), 'Accept All') or contains(text(), 'Continue') or contains(text(), 'Accept All Cookies') or contains(text(), 'Allow All')]"
    accept_button = None
    wait = WebDriverWait(driver, 3)
    try:
        accept_button = driver.find_element(By.XPATH, accept_button_xpath)
    except NoSuchElementException:
        pass
    if accept_button and accept_button.is_displayed():
        accept_button.click()
    viewport_height = driver.get_window_size()["height"]
    webpage_height = driver.execute_script(
        "return document.body.parentNode.scrollHeight"
    )
    no_images = math.floor(webpage_height / (viewport_height - 280))
    cropped_images = []
    for i in range(no_images):
        time.sleep(slpt2)
        driver.execute_script(f"window.scrollTo(0, {i*(viewport_height-280)});")
        driver.save_screenshot(f"screenshots/screenshot{i}.png")
        time.sleep(slpt1)
    try:
        image1 = cv2.imread(f"screenshots/screenshot{int(no_images/2)}.png")[:, :-80]
        image2 = cv2.imread(f"screenshots/screenshot{int(no_images/2 + 1)}.png")[
            :, :-80
        ]
        driver.quit()
        cropped_images = crop_screenshots(
            cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY),
            cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY),
            no_images,
        )
    except Exception:
        try:
            chrome_options = Options()
            driver = webdriver.Chrome(options=chrome_options)
            chrome_options.add_argument("--ignore-certificate-errors")
            driver.get(f"https://doi.org/{doi}")
            viewport_height = driver.get_window_size()["height"]
            webpage_height = driver.execute_script(
                "return document.body.parentNode.scrollHeight"
            )
            no_images = math.floor(webpage_height / (viewport_height - 280))
            cropped_images = []
            for i in range(no_images):
                driver.execute_script(f"window.scrollTo(0, {i*(viewport_height-280)});")
                driver.save_screenshot(f"screenshots/screenshot{i}.png")
            if os.path.exists("screenshots/screenshot2.png"):
                image1 = cv2.imread(f"screenshots/screenshot{int(no_images/2)}.png")[
                    :, :-80
                ]
            if os.path.exists("screenshots/screenshot2.png"):
                image2 = cv2.imread(
                    f"screenshots/screenshot{int(no_images/2 + 1)}.png"
                )[:, :-80]
            driver.quit()
            cropped_images = crop_screenshots(
                cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY),
                cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY),
                no_images,
            )
        except Exception:
            driver.quit()
            for i in range(no_images):
                if os.path.exists("screenshots/screenshot2.png"):
                    img = cv2.imread(f"screenshots/screenshot{i}.png")
                    cropped_images.append(img)
    image = cv2.vconcat(cropped_images)
    cv2.imwrite(name, image)


# my students wrote this part, but I think it is looking for differences in adjacent screenshots, cropping overlaps, then stitchign together
def crop_screenshots(base_img1, base_img2, no_images):
    difference = (
        structural_similarity(base_img1, base_img2, full=True)[1] * 255
    ).astype("uint8")
    thresh = cv2.threshold(difference, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[
        1
    ]
    contours = imutils.grab_contours(
        cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    )
    regions = []
    for contour in contours:
        (x, y, width, height) = cv2.boundingRect(contour)
        region = [x, y, x + width, y + height]
        regions.append(region)
    top = min([region[1] for region in regions])
    bottom = max([region[3] for region in regions])
    left = min([region[0] for region in regions])
    right = max([region[2] for region in regions])
    cropped_images = []
    for i in range(no_images):
        if os.path.exists("screenshots/screenshot2.png"):
            img = cv2.imread(f"screenshots/screenshot{i}.png")[top:bottom, left:right]
            cropped_images.append(img)
    return cropped_images


# this function uses OCR (tesseract) to convert stitched image of text into plain text file for storage
def generateText(i):
    try:
        img = cv2.imread(f"img_results/{i}file.png")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, thresh1 = cv2.threshold(
            gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV
        )
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (12, 12))
        dilation = cv2.dilate(thresh1, rect_kernel, iterations=3)
        cv2.imwrite("test.png", dilation)
        contours, hierarchy = cv2.findContours(
            dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
        )
        im2 = img.copy()
        open(f"text_results/{i}text_output.txt", "w").close()
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            cropped = im2[y : y + h, x : x + w]
            file = open(f"text_results/{i}text_output.txt", "a")
            file.write(pytesseract.image_to_string(cropped).lower())
            file.close()
    except Exception as e:
        file = open(f"text_results/{i}text_output.txt", "w")
        file.write(str(e))
        file.close()


# this function generates the full citation info for each manuscript that matches the pubmed search and will be used later in emailed output
def generate_citation(candidates, doi):
    citation = ""
    info = candidates[doi]
    authors = info["authors"]
    auths = []
    for author in authors:
        auths.append(author["lastname"])
        if author["firstname"] is None:
            continue
        original_initials = author["initials"]
        initials = ""
        if len(original_initials) > 1:
            initials = f"{original_initials[0]}. {original_initials[1]}."
        else:
            initials = original_initials + "."
        citation += f"{author['lastname']}, {initials}; "
    citation = f"{citation[:-2]} {info['title']} {info['journal']}. {info['publication_date'].strftime('%Y')}. https://doi.org/{doi}.\n"
    return citation, author, auths


#### MAIN CODE STARTS HERE

# TODO If this is just here to create the file, it's not really necessary. It will overwrite any existing annual.txt file with an empty file, which could be bad.  -VP
open("annual.txt", "w").close()  # this will store all of the manscrupts for each year

# Makes the output folder structure, removing any existing folders and all their contents -VP
folder_names = ["img_results", "text_results", "screenshots"]
for folder_name in folder_names:
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    os.mkdir(folder_name)


# with open(
#     "data.txt", "r"
# ) as f:  # this file should be created from a webform or manually - csv file with needed info (but also some leftover junk that can be pruned)
#     reader = csv.reader(f, delimiter="|")
#     for row in reader:
#         subname = row[0]
#         subemail = row[1]
#         orcid = row[2]
#         affiliation = row[3]
#         town = row[4]
#         supwords = row[5]
#         startdate = row[6]
#         enddate = row[7]
#         reqterms = row[8]

# # The terms variable is unused, so this block can be removed -VP
# with open("data.txt", "r") as f:
#     reader = csv.reader(f, delimiter="|")
#     terms = list(reader)

# Note that dates MUST be in YYYY/MM/DD, YYYY or YYYY/MM format, see https://www.ncbi.nlm.nih.gov/books/NBK25499/ for reference -VP
# HARD CODED BY VIRGINIA FOR TESTING, can be removed later: -VP
startdate = "2024/05/01"
enddate = "2024/06/01"
affiliation = "University of Massachusetts Amherst"
town = "Amherst"

daterange = startdate + ":" + enddate
print("DATE: ", daterange)

affiliation = re.sub("[^0-9a-zA-Z]+", "+", affiliation)
print("AFFL: ", affiliation)
search_query = f"{affiliation}+[ad]+{town}+[ad]+{daterange}+[dp]"

# Note that I tried using the urllib.parse functionality to encode the url, but it doesn't work. Next two lines are my suggested code changes. - VP
# raw_query = f"({daterange}[DP])AND({affiliation}[AD])"
# search_query = re.sub(r"\s+", "+", raw_query)


print("SRCH: ", search_query)
# This is only searching for the last affiliation that appeared in the last row of the CSV file. Is that intentional? -VP
candidates, candidates_doi, no_of_candidates, articles_df = search(search_query, 100000)

articles_df.to_csv("pubmed_search_results.csv", index=False)
end = no_of_candidates

# TODO Could use tqdm for showing progress
# Judge manuscript qualtiy based on stitched screenshot length
for i in range(end):
    try:
        a1, a2, auths = generate_citation(candidates, candidates_doi[i])
        # print("Downloading", i + 1, "of", end)
        raise KeyError
        # download(candidates_doi[i], f"img_results/{i}file.png")
        # image_height = cv2.imread(f"img_results/{i}file.png").shape[0]
        # if (
        #     image_height < 8000
        # ):  # these are manuscripts that were PROBABLY not successful
        #     print("SHORTY")
        #     with open("annual.txt", "a") as f:
        #         f.write(f"{i}|shorty-download|{a1}")
        #     print("Transcribing now...")
        #     generateText(i)
        #     path = os.getcwd()
        #     path = os.path.join(path, "text_results", f"{i}text_output.txt")
        # else:
        #     print("GOOD ONE")
        #     with open("annual.txt", "a") as f:
        #         f.write(f"{i}|sucess-download|{a1}")
        #     print("Transcribing now...")
        #     generateText(i)
        #     path = os.getcwd()
        #     path = os.path.join(path, "text_results", f"{i}text_output.txt")
    except Exception as e:  # these are manuscripts that were certainly not successful
        # print("ERROR", e)
        with open("annual.txt", "a") as f:
            f.write(f"{i}|failed-download|{a1}")
