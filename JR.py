import urllib2
import urllib
import json

_browser ={}
_baseUrl = ""
_loginUrl = ""
def loginJira(url,username,password):
	global _browser,_baseUrl,_loginUrl
	if _browser != {}:
		return 
	_baseUrl = url
	_loginUrl ="%s%s" % (_baseUrl,"/login.jsp") 
	_browser = urllib2.build_opener(urllib2.HTTPCookieProcessor())
	loginForm = {"os_username":username, "os_password":password, "os_destination":"", "alt_token":"", "login":"Log In"}
	loginForm = urllib.urlencode(loginForm)
	request = urllib2.Request(_loginUrl)
	response = _browser.open(request, loginForm)
	print "Login successfully."
	return response

def Read(jiraNumber):
	global _browser,_baseUrl
	requestUrl = "%s/rest/api/2/issue/%s" % (_baseUrl, jiraNumber)
	request = urllib2.Request(requestUrl)
	response = _browser.open(request)
	#print response.headers.headers
	#all data will be reposne in one line
	line = response.readline()
	#print line
	return json.loads(line)

def ReadSummary(jiraNumber):
	jsonData = Read(jiraNumber)
	return jsonData

def ReadKeysWithoutPoints(project = 12950, num=2000):
	global _browser, _baseUrl
	template = "\"Story Points\" = NULL AND project = %d" % project
	data = {"maxResults":num,"fields":"key","jql":template}
	searchUrl = "%s/rest/api/2/search?%s" % (_baseUrl, urllib.urlencode(data))
	request = urllib2.Request(searchUrl)
	response = _browser.open(request)
	return json.loads("".join(response.readlines()))

def Go(jiraBaseAddress,username, password):
	import sys
	reload(sys)
	sys.setdefaultencoding("utf8")
	loginJira(jiraBaseAddress,username,password)
	ids= ReadKeysWithoutPoints()
	keys=[]
	for id in ids["issues"]:
		keys.append(id["key"])
	print keys
	for jiraNumber in keys:
		summary = ReadSummary(jiraNumber)
		print "======================%s=====================" % jiraNumber
		print "Summary: %s" % summary["fields"]["summary"].encode("utf8")
		print "Assignee: %s" % summary["fields"]["assignee"]["displayName"].encode("utf8")
		description = summary["fields"]["description"] 
		if description != None:
			print "Description: %s" % description.encode("utf8")
		comment = summary["fields"]["comment"]
		if comment != None:
			if len(comment["comments"])>0:
				for commentline in comment["comments"]:
					print "%s: %s" % (commentline["author"]["displayName"].encode("utf8"), commentline["body"].encode("utf8"))
		nPoint = raw_input("New Point: ")
		if nPoint == "":
			print "Ignore"
			continue
		else:
			UpdatePoint(jiraNumber, round(float(nPoint),1))

def UpdatePoint(jiraNumber, point):
	global _baseUrl, _browser
	try:
		requestUrl = "%s/rest/api/2/issue/%s" % (_baseUrl, jiraNumber)
		request  = urllib2.Request(requestUrl)
		request.get_method= lambda:"PUT"
		request.headers["Content-Type"]="application/json"
		requestData = {"fields":{"customfield_10992":point}}
		response = _browser.open(request, json.dumps(requestData))
	except Exception, e:
		print e.msg
		print e.hdrs
		return e.fp
	
