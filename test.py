import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException
import time

# Set up the driver
driver = webdriver.Chrome()
driver.maximize_window()

# Open the webpage
driver.get('https://greenbook.nafdac.gov.ng/')

columns = [
    "Product Name", "Active Ingredient", "Product Category", "NRN", "Form", "ROA", 
    "Strengths", "Applicant's Name", "Approval Date", "Status"
]
data = pd.DataFrame(columns=columns) 

dropdown_element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.NAME, "DataTables_Table_0_length"))
)
select = Select(dropdown_element)
select.select_by_value('100') 

time.sleep(5) 

page_number = 1
# # Skip first 17 pages
# for _ in range(page_number):
#     try:
#         # Handle any unexpected alerts
#         try:
#             alert = driver.switch_to.alert
#             alert.accept()  # Accept the alert
#             print("Handled unexpected alert.")
#         except:
#             pass  # No alert, continue

#         # Find and click the "Next" button
#         page_button = driver.find_element(By.XPATH, "//a[@aria-controls='DataTables_Table_0' and text()='Next']")
#         driver.execute_script("arguments[0].click();", page_button)
#         time.sleep(2)
#     except Exception as e:
#         print(f"Error navigating through pages: ")
#         break  # Exit the loop if there's an issue


while True:
    try:
        try:
            alert = driver.switch_to.alert
            alert.accept()
            print("Handled unexpected alert.")
        except:
            pass 

        rows = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, "//table/tbody/tr"))
        )
        
        temp_data = [] 
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            row_data = []

            for index, col in enumerate(cols):
                if col.find_elements(By.TAG_NAME, "a"):
                    link_text = col.find_element(By.TAG_NAME, "a").text.strip()
                    row_data.append(link_text)
                else:
                    row_data.append(col.text.strip() if col.text.strip() != '' else 'N/A')
                
            if len(row_data) < len(columns):
                row_data.extend(['N/A'] * (len(columns) - len(row_data)))

            temp_data.append(row_data)
        
        temp_df = pd.DataFrame(temp_data, columns=columns)
        data = pd.concat([data, temp_df], ignore_index=True)

        data.to_excel("final_output_data.xlsx", index=False)
        print(f"Saved {len(data)} rows to final_data.xlsx")

        try:
            next_button = driver.find_element(By.XPATH, "//a[@aria-controls='DataTables_Table_0' and text()='Next']")
            if 'disabled' in next_button.get_attribute('class'):
                print("No more pages to process.")
                break
            else:
                driver.execute_script("arguments[0].click();", next_button)
                print(f"Processing next page... {page_number}")
                if page_number > 65:
                    break
                page_number+=1
                time.sleep(5)
        except Exception as e:
            print(f"Error clicking next button:")
            break

    except UnexpectedAlertPresentException as e:
        print(f"Unexpected alert encountered:")
        alert = driver.switch_to.alert
        alert.accept() 
        time.sleep(2)

data.to_excel("final_output_data.xlsx", index=False)
print(f"Final save: {len(data)} rows saved to final_data.xlsx")

driver.quit()
print("Data extraction complete.")
