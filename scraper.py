from bs4 import BeautifulSoup
import requests
import pandas as pd

# NOTE: I dont really think I need to specify a function paramater with a type, but I like the pretty colors.
def scrape_employee_data(URL:str):

    card_columns = ['emp_first_name', 'emp_second_name', 'emp_email', 'emp_ssn',    'emp_phone_number_???',]
    contact_information_dataframe = pd.DataFrame(columns=card_columns)
    
    print(f"Accessing {URL}")
    page = requests.get(URL)
    
    print("Extracting soup")
    soup = BeautifulSoup(page.text, 'lxml')

    exposed_contact_cards = [data for data in soup.find_all('div', class_ = "card employee")]

    print("Straining soup")
    for exposed_card in exposed_contact_cards:
        employee_card_data = [row.text.strip() for row in exposed_card.find_all('span')]

        maybe_a_phone_number = exposed_card.get_text()

        # NOTE: Phone number  mess is not contained in its own div. Cant use .text on parent div because it returns all the other information. Got tired of trying to find some fancy way to isolate the string with bs4. Used the following monstrosity to butcher the larger .text return. Enjoy.

        # What do you want from me? Its late. I seek the sweet comfort of my bed.
        
        employee_card_data.append(maybe_a_phone_number[maybe_a_phone_number.find('.com'):-11].lstrip    ('.com'))

        length = len(contact_information_dataframe)
        contact_information_dataframe.loc[length] = employee_card_data

    print("Putting leftover soup in the fridge because who the hell eats this much soup?!")
    contact_information_dataframe.to_csv(r'./employee_data.csv', index=False)
    
def main():
    scrape_employee_data("https://cit30900.github.io/strawbridge/")
    
if __name__ == "__main__":
    main()
    
