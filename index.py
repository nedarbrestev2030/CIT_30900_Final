import csv
from bs4 import BeautifulSoup
import requests

def scrape_employee_data(URL:str):
    print(f"ACTION: Retrieving content from {URL}")
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, 'lxml')
    
    print(f"ACTION: Extracting data from HTML")
    exposed_contact_cards = [data for data in soup.find_all('div', class_ = "card employee")]
    
    print(f"ACTION: Writing data to employee_data.csv")
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
    
    print(f"ACTION: Copying data from {cliEmpCSV}")
    print(f"ACTION: Checking employee SSN exposure level")
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
    
    print(f"ACTION: Composing client risk report, employee_risk.csv")
    with open("employee_risk.csv", "w", newline='') as csvfile:
        fieldnames = ["first_name", "last_name", "email", "ssn", "risk_level"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for emp in employee_exposure_checks:
            writer.writerow(emp)
    csvfile.close()
    
def analyse_exposure_report(report):
    
    print(f"ACTION: Copying data from {report}")
    with open(report, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        check_results = []
        for row in reader:
            check_result = {
                "employee":f'{row["first_name"]}_{row["last_name"]}',
                "email":row["email"],
                "exposure_level":row["risk_level"]
            }
            check_results.append(check_result)
    csvfile.close()
    
    exposure_counts = {
        "low":0,
        "medium":0,
        "high":0
    }
    
    print(f"ACTION: Summarizing exposure results")
    for result in check_results:
        if result["exposure_level"] == "low":
            exposure_counts["low"]+=1
        elif result["exposure_level"] == "medium":
            exposure_counts["medium"]+=1
        elif result["exposure_level"] == "high":
            exposure_counts["high"]+=1
            
            emp_name_split = (result["employee"].split("_"))
            
            print(f"ACTION: Composing high risk email for {result['employee']}")
            with open(f"{result['employee']}.txt", 'w') as file:
                exposure_notice_email = f"""
Dear {emp_name_split[0]+ ' ' + emp_name_split[1]},
               
Your personal data was accidentally exposed on the Strawbridge Industries website and is at risk of being compromised. The company regrets this error and would like to offer a credit monitoring service at no cost to you. Please contact HR to establish this service.
                
Thank you,
Dick Strawbridge, CEO"""
                
                file.writelines(exposure_notice_email)
        else:
            print("MESSAGE: Result missing exposure level")
            
            file.close()

    print ("________________________________________")            
    print(f"Low risk exposures detected : {exposure_counts['low']}")
    print(f"Medium risk exposures detected : {exposure_counts['medium']}")
    print(f"High risk exposures detected : {exposure_counts['high']}")
    
def main():
    scrape_employee_data("https://cit30900.github.io/strawbridge/")
    create_csv_report("employee_data.csv")
    analyse_exposure_report("employee_risk.csv")
    
if __name__ == "__main__":
    main()
    
    
# TODO: Add stats messages
    
# NOTE: On occasion, receive following error. Investigate.

# raise ConnectionError(err, request=request)
# requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))