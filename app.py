import os
from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)
emails = []
websites = []
none = []

class Nonprofit(object):
	"""docstring for Nonprofit"""
	def __init__(t, nonprofit_string):
		super(Nonprofit, t).__init__()
		properties = ["ein","name","url","year","person","addr1","addr2","city","state"]
		nonprofit_details = nonprofit_string.split("|")
		t.string = nonprofit_string
		t.ein = nonprofit_details[0].strip()
		t.name = nonprofit_details[1].strip()
		t.url = nonprofit_details[2].strip().lower()
		t.year = nonprofit_details[3].strip()
		t.person = nonprofit_details[4].strip()
		t.addr1 = nonprofit_details[5].strip()
		t.addr2 = nonprofit_details[6].strip()
		t.city = nonprofit_details[7].strip()
		t.state = nonprofit_details[8].upper().strip()
		t.full_addr = "{0} {1}, {2}, {3}".format(t.addr1, t.addr2, t.city, t.state)
		t.ein = "0"+t.ein  if (len(t.ein)==8) else t.ein

	def match(t, name, city, state):
		res =  t.name.lower().find(name.lower()) > -1 and \
			t.city.lower().find(city.lower()) > -1 and \
			t.state.lower().find(state.lower()) > -1
		return res


with open("emails.csv", "r") as f:
    emails = [ Nonprofit(l.strip().decode("utf8")) for l in f.readlines() if len(l) > 5]

with open("websites.csv", "r") as f:
    websites = [ Nonprofit(l.decode("utf8").strip()) for l in f.readlines() if len(l) > 5]

with open("none.csv", "r") as f:
    none = [ Nonprofit(l.strip().decode("utf8")) for l in f.readlines() if len(l) > 5]


@app.route('/')
def index():
	return render_template("index.html")

@app.route('/api/', methods=['GET'])
def api():
	name = request.args.get('name', "")
	city = request.args.get('city', "")
	state = request.args.get('state', "")
	if (name == "" and city == "" and state == ""):
		return "<b> You must specify a name, city or state</b>"
	include_none = request.args.get('include_none', False)
	my_emails = [nonprofit for nonprofit in emails if nonprofit.match(name, city, state)]
	my_websites = [nonprofit for nonprofit in websites if nonprofit.match(name, city, state)]
	my_none = [nonprofit for nonprofit in none if nonprofit.match(name, city, state)] if include_none else []
	return render_template("api_results.html", my_emails=my_emails, my_websites=my_websites, my_none=my_none, include_none=include_none)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9000, debug=True)
