import csv
from bs4 import BeautifulSoup
import requests

def scrape_employee_data(URL:str):
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, 'lxml')
    exposed_contact_cards = [data for data in soup.find_all('div', class_ = "card employee")]
    
    with open("employee_data.csv", "w", newline='') as csvfile:
        fieldnames = ['emp_first_name', 'emp_last_name', 'emp_email', 'emp_ssn', "emp_phone"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for exposed_card in exposed_contact_cards:
            employee_data_raw = [item.text for item in exposed_card.find_all("span")]
            employee_data = {
                'emp_first_name' : employee_data_raw[0],
                'emp_last_name' : employee_data_raw[1],
                'emp_email' : employee_data_raw[2],
                'emp_ssn' : employee_data_raw[3],
            }
            
            phone_unclear = exposed_card.get_text()
            phone_clear = phone_unclear[phone_unclear.find('.com'):-11].lstrip('.com')
            
            employee_data["emp_phone"] = phone_clear
            
            writer.writerow(employee_data)
    csvfile.close()
        
        
def check_ssn_risk_level(ssn:str)->str:
    API_response = requests.get(f"https://us-central1-cit-37400-elliott-dev.cloudfunctions.net/have-i-been-pwned?username=elliott&ssn={ssn}").json()
    
    return API_response["exposure"]

def create_csv_report(cliEmpCSV:str):
    employee_exposure_checks=[]
    
    with open(cliEmpCSV, "rt") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            employee_exposure_check = {
                "first_name":row["emp_first_name"],
                "last_name":row["emp_last_name"],
                "email":row["emp_email"],
                "ssn":row["emp_ssn"]
            }
            
            employee_exposure_check["risk_level"] = check_ssn_risk_level(employee_exposure_check["ssn"])
            
            employee_exposure_checks.append(employee_exposure_check)
    csvfile.close()
    
    with open("employee_risk.csv", "w", newline='') as csvfile:
        fieldnames = ["first_name", "last_name", "email", "ssn", "risk_level"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for emp in employee_exposure_checks:
            writer.writerow(emp)
    csvfile.close()
    

def main():
    scrape_employee_data("https://cit30900.github.io/strawbridge/")
    create_csv_report("employee_data.csv")
    
if __name__ == "__main__":
    main()
    
    
# NOTE: On occasion, receive following error. Investigate.

# raise ConnectionError(err, request=request)
# requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))