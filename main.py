from datetime import datetime, timedelta
from functions import *
import csv


hearing_date_search_url = 'https://eapps.courts.state.va.us/gdcourts/caseSearch.do?fromSidebar=true&searchLanding' \
                          '=searchLanding&searchType=hearingDate&searchDivision=V&searchFipsCode=510&curentFipsCode=510'
# get date
cleaned_today = datetime.today().strftime('%m-%d-%Y')
# output file names
hearing_scrape_file = f'files/hearings_scraped_on_{cleaned_today}.csv'
summary_scrape_file = f'files/summary_scraped_on_{cleaned_today}.csv'

# create browser
browser = webdriver.Chrome()

# write headers for case output file
with open(hearing_scrape_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(create_headers())

# date range - number of days backwards, and number of days forwards
date_range = 70
start_date = datetime.today() - timedelta(date_range)
date_list = [start_date + timedelta(days=x) for x in range(date_range * 2)]


rows_to_write = []
for date in date_list:
    while browser.current_url != hearing_date_search_url:
        browser.get(hearing_date_search_url)
    # enter date and search
    browser.find_element(By.ID, 'txthearingdate').send_keys(date.strftime('%m/%d/%Y'))
    browser.find_element(By.NAME, 'caseSearch').click()
    # print searched date
    print(date.strftime('%m/%d/%Y'))
    # count of cases scraped
    count = 0
    case_nums = []
    # get rows of cases
    rows = browser.find_elements(By.CSS_SELECTOR, 'tr.evenRow, tr.oddRow')
    for row in rows:
        td_list = []
        # get table data cells of each row
        tds = row.find_elements(By.CSS_SELECTOR, "td.gridrow")
        # check if case is unlawful detainer
        if tds[4].text == "Unlawful Detainer":
            # splice to remove checkbox
            for td in tds[1:]:
                td_list.append(td.text)
            td_list.append(date.strftime('%m/%d/%Y'))
            rows_to_write.append(td_list)
            case_nums.append(tds[1].text)

    # scrape hearings
    with open(hearing_scrape_file, 'a', newline='') as file:
        writer = csv.writer(file)
        for num in case_nums:
            writer.writerow(hearing_scrape(num))
            count += 1
            print(f'scraped cases on page: {count}')
    print(f'total scraped on page = {count}')

# write to summary scrape output file
with open(summary_scrape_file, 'w', newline='') as summary:
    writer = csv.writer(summary)
    headers = ['case_number', 'defendant', 'plaintiff', 'case type', 'hearing time', 'date']
    writer.writerow(headers)
    writer.writerows(rows_to_write)
