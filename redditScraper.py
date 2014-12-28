import requests
import re
import time

from bs4 import BeautifulSoup


# A generalized Reddit webScraper that takes in a Subreddit name, search topic,
# key word, upvote threshold, and number of search results in order to deliver a neatly
# organized list of the top posts in the form of a CSV file. 


# Performs the HTTP request and saves the BeautifulSoup object.
def makeRequest(site, payload):
	response = requests.get(site, params = payload)
	soup = BeautifulSoup(response.content)
	return soup

# Performs a request based on the given search parameter and searchFor, which designates
# a single keyword relevant to the user's interests. 
def requestWithParam(subreddit, param, searchFor, numResults, threshold):

	# Search through Reddit's results 25 per page.
	perPage = 25

	site = 'http://www.reddit.com/r/' + subreddit + '/search'

	# The search parameters. 
	payload = {
		'q' : param,
		'restrict_sr' : 'on',
		'count' : 0,
		'sort' : 'relevance',
		't' : 'all'
	}

	results = []

	while (payload['count'] <= numResults):

		soup = makeRequest(site, payload)

		# Varies based on structure of the site. Here I am searching through Reddit's posts flagged by their
		# score and relevancy to my search. 
		for score in soup.find_all('div', class_ = "score likes"):

			row = []

			rating = int(score.string)
			if (rating > threshold):
				parent = score.parent.parent
				for title in parent.find_all('a', class_ = "title"):
					if (findWholeWord(searchFor)(title.string)):
						row.append(title.string)
						row.append(title.get('href'))
						row.append(rating)
						results.append(row)

		payload['count'] += perPage
		# Otherwise it would look like I'm DDOS'ing Reddit.
		time.sleep(3)

	# writeResults(results)

	return results

# Writes our results to a CSV file for easy access and readability. 
def writeResults(results):

	outfile = open("./Results.csv", "wb")
	writer = csv.writer(outfile)
	writer.writerow(["URL", "Title", "Rating"])
	writer.writerows(results)

# Collects user input to be used as the search parameter and searchable keyword.
def collectRequest():

	subreddit = input("Please enter the subreddit you're interested in: ")
	param = input("Please enter what topic you would like to search for: ")
	searchFor = input("Please enter the specific keyword you would like to monitor: ")
	numResults = input("Please enter the total number of items you want to search: ")
	threshold = input("Please enter the minimum score threshold for your results: ")

	return subreddit, param, searchFor, numResults, threshold

###################
# UTILITY METHODS #
###################

# Uses RegEx to search for a specific word in a string, ignoring case. Will help us later when
# attempting to determine what information is relevant based on the titles of our results.
def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

# Turns the returned list into ASCII as opposed to the unicode produced by BeautifulSoup.
# Only necessary when returning a list of Strings, otherwise you may manage the data as you wish.
def encodeProperly(results):

	readable_list = []

	for innerList in results:
		for item in innerList:
			try:
				if (type(item) is not int):
					readable_list.append(item.encode("ascii"))
				else:
					readable_list.append(item)
			except UnicodeError:
				continue

	return readable_list

# The starting point for this project.
def main():

	try: 
		while True:	
			subreddit, param, searchFor, numResults, threshold = collectRequest();
			results = encodeProperly(requestWithParam(subreddit, param, searchFor, numResults, threshold))
			if (len(results) > 0):
				print(results)
			else:
				print("The search produced no results, or you may be sending requests too frequently.")

			shouldContinue = input("If you would like to search for more results, please enter 'y'. Otherwise, press any key to exit. ")

			if (shouldContinue != 'y'):
				break

	except NameError, SyntaxError:
		print("Please enter inputs with quotes around them. Try again!")
		main()

main()
