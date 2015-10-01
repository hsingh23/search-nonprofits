import os
from flask import Flask

app = Flask(__name__)
emails = []
websites = []

with open("emails.csv", "r") as f:
    emails = [ l.strip().decode("utf8") for l in f.readlines()]

with open("websites.csv", "r") as f:
    websites = [ l.decode("utf8").strip() for l in f.readlines()]

@app.route('/')
def index():
    return 'Search nonprofits with email and website by adding your search term after the / <br> You can also search a city using /city/City Name'

@app.route('/<search>')
def simple_search(search):
    search = search.lower()
    filtered_emails = "<br>".join([ l for l in emails if search in l.lower()  ])
    filtered_websites = "<br>".join([ l for l in websites if search in l.lower()  ])

    matches = """
    <h2> ein(IRS identification number)|organization_name|officer_address_city|organization_address_state|officer_name|email </h2>
    <h1> Emails </h1>
    %s
    <br>
    <br>
    <h1> Websites </h1>
    %s
    """ % (filtered_emails, filtered_websites)
    return matches

@app.route('/city/<search>')
def city_search(search):
    search = "|"+search.lower()+"|"
    filtered_emails = "<br>".join([ l for l in emails if search in l.lower()  ])
    filtered_websites = "<br>".join([ l for l in websites if search in l.lower()  ])

    matches = """
    <h2> ein(IRS identification number)|organization_name|officer_address_city|organization_address_state|officer_name|email </h2>
    <h1> Emails </h1>
    %s
    <br>
    <br>
    <h1> Websites </h1>
    %s
    """ % (filtered_emails, filtered_websites)
    return matches



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9000, debug=True)
