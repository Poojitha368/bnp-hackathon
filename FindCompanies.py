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
    pass