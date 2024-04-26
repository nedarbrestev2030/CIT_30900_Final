import csv
from bs4 import BeautifulSoup
import requests

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
                "last_name":row["emp_second_name"],
                "email":row["emp_email"],
                "ssn":row["emp_ssn"]
            }
            
            employee_exposure_check["risk_level"] = check_ssn_risk_level(employee_exposure_check["ssn"])
            
            employee_exposure_checks.append(employee_exposure_check)
    csvfile.close()
    
    with open("employee_risk.csv", "w") as csvfile:
        fieldnames = ["first_name", "last_name", "email", "ssn", "risk_level"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for emp in employee_exposure_checks:
            writer.writerow(emp)
    csvfile.close()
    

def main():
    create_csv_report("employee_data.csv")

    # check ssn with api
    # 
    
    # print(API_response["exposure"])
    
if __name__ == "__main__":
    main()