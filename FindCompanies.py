import requests
import streamlit as st

API_KEY = "d376tm1r01qtvbtkcj00d376tm1r01qtvbtkcj0g"
URL = f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={API_KEY}"

def FetchCompanies():
    response = requests.get(URL)
    company_list = response.json()

    companies = [company['symbol'] for company in company_list]

    return companies

def FilterCompanies(companies):
    st.header("Choose a Company")

    #serach with inputbox
    '''search = st.text_input("search a company")
    filtered = [company for company in companies if search.lower() in company.lower()]

    company = st.selectbox("Matching Companies", filtered) if filtered else None

    if company:
        st.write(f"You selected {company}")
    else:
        st.write("No company found")
    '''
    return company