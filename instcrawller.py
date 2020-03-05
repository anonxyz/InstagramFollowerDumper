import pycurl
import io
import sys
from bs4 import BeautifulSoup
import re
import time
import os

session=""    #put your user session here!!


def biodumper():
	fp2=open("dump2.txt","w")	
	with open("dump1.txt","r") as fp:
		for username in fp:
			b_obj=io.BytesIO()
			crl=pycurl.Curl()
			url="https://www.instagram.com/"+username.strip()+"/"
			crl.setopt(crl.URL,url)
			print("\n\n\n"+url+"\n")
			fp2.write("\n\n\n"+url+"\n")
			crl.setopt(crl.WRITEDATA,b_obj)
			crl.setopt(crl.USERAGENT,"Mozilla/5.0 (X11; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0")
			crl.setopt(crl.COOKIE,"sessionid="+session)
			crl.perform()
			crl.close()
			getdata=b_obj.getvalue()
			html=getdata.decode('utf-8')
			#start extracting information here
			result=[m.start() for m in re.finditer("biography",html)]
			i=12
			strstart=result[1]
			usernamedump=""
			while(html[strstart+i])!="\"":
				usernamedump+=html[strstart+i]
				print(html[strstart+i],end="")
				i+=1
			fp2.write(usernamedump+"\n\n----------------------------------------------------")
	print("All bio has succesfully been dumped")
	fp2.close()
	sys.exit()

def getrestoftheusernames(idnum,edge,followersgot,total_followers):
	print("FOLLOWERS_GOT : "+str(followersgot))
	print("TOTAL FOLLOWERS : "+str(total_followers))
	if (int(total_followers)==int(followersgot)):
		print("ALL FOLLOWERS EXTRACTED")
		answer=input("would you like to to dump information on the follower that were extracted? Y/N\n")
		answer=answer.lower()
		if answer == 'y':
			print("ok")
			biodumper()
		else:
			sys.exit(0)
	print("Trying to get rest of the usernames")
	print(idnum)
	print(edge)
	url="https://www.instagram.com/graphql/query/?query_hash=d04b0a864b4b54837c0d870b0e77e076&variables={\"id\":\""+idnum+"\",\"include_reel\":true,\"fetch_mutual\":false,\"first\":12,\"after\":\""+edge+"\"}"
	print(url)
	b_obj=io.BytesIO()
	crl=pycurl.Curl()
	crl.setopt(crl.URL,url)
	crl.setopt(crl.WRITEDATA,b_obj)
	crl.setopt(crl.USERAGENT,"Mozilla/5.0 (X11; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0")
	crl.setopt(crl.COOKIE,"sessionid="+session)
	crl.perform()
	crl.close()
	getdata=b_obj.getvalue()
	html=getdata.decode('utf-8')
	#extracing the end_cursor
	next_edge=""
	result=[m.start() for m in re.finditer("end_cursor",html)]
	start=result[0]
	i=13
	while(html[start+i]!="\""):
		next_edge+=html[start+i]
		i=i+1
	print(next_edge)
	#starting the extraction of usernames
	result.clear()
	result=[m.start() for m in re.finditer("username",html)]
	updated_list=updatelist(result)
	length=len(updated_list)
	print("FOUND USERNAMES : "+str(length))
	followersgot+=length
	fp=open("dump1.txt","a")
	for listnum in updated_list:
		username=""
		start=11
		while(html[listnum+start]!="\""):
			username+=html[listnum+start]
			start+=1
		fp.write(username+"\n")
	print("FOLLOWERS GOT SO FAR : "+str(followersgot))
	fp.close()
	getrestoftheusernames(idnum,next_edge,followersgot,total_followers)


def updatelist(list):
	del list[::2]
	return  list

def getinitfollowers(idnum):
	followersgot=""
	time.sleep(2)
	print("Trying to get initial follower on id :"+idnum)
	url="https://www.instagram.com/graphql/query/?query_hash=d04b0a864b4b54837c0d870b0e77e076&variables={\"id\":\""+idnum+"\",\"include_reel\":true,\"fetch_mutual\":false,\"first\":24}"
	print(url)
	b_obj=io.BytesIO()
	crl=pycurl.Curl()
	crl.setopt(crl.URL,url)
	crl.setopt(crl.WRITEDATA,b_obj)
	crl.setopt(crl.USERAGENT,"Mozilla/5.0 (X11; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0")
	crl.setopt(crl.COOKIE,"sessionid="+session)
	crl.perform()
	crl.close()
	getdata=b_obj.getvalue()
	html=getdata.decode('utf-8')
	result=[m.start() for m in re.finditer("count",html)]
	start=result[0]
	i=7
	total_followers=""
	while(html[start+i]!=","):
		total_followers+=(html[start+i])
		i=i+1
	print("The user is following : "+total_followers+" people")
	#finding edge using re-itter
	edge=""
	result.clear()
	result=[m.start() for m in re.finditer("end_cursor",html)]
	start=result[0]
	i=13
	while(html[start+i]!="\""):
		edge+=html[start+i]
		i=i+1
	print(edge)
	#extraction of FIRST 22 followers
	result.clear()
	result=[m.start() for m in re.finditer("username",html)]
	#update the list before calling print on the list


	#print(str(result))
	print(str(len(result)))
	updatedlist=updatelist(result)
	print(str(updatedlist))
	followersgot=len(updatedlist)
	#print the first set of usernames(28)
	if os.path.isfile("dump1.txt"):
		print(" dump1 exists.Removing the file")
		os.remove("dump1.txt")
	fp=open("dump1.txt","a")		


	for listnum in updatedlist:
		username=""
		start=11
		while(html[listnum+start]!="\""):
			username+=html[listnum+start]
			start+=1
		fp.write(username+"\n")
	#now get the rest of the usernames by recursively calling it and
	#passing idnum and end_cursor
	fp.close()
	getrestoftheusernames(idnum,edge,followersgot,total_followers)

def initgetrequest():
	print("Trying to send the initial request")
	b_obj=io.BytesIO()
	crl=pycurl.Curl()
	crl.setopt(crl.URL,sys.argv[1])
	crl.setopt(crl.WRITEDATA,b_obj)
	crl.setopt(crl.USERAGENT,"Mozilla/5.0 (X11; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0")
	crl.setopt(crl.COOKIE,"sessionid="+session)
	crl.perform()
	crl.close()
	get_body=b_obj.getvalue()
	htmldoc=get_body.decode('utf-8')
	print("Now extracting the vitim id number to further request")
	result=[m.start() for m in re.finditer("\"id\":\"",htmldoc)]
	if len(result)<3:
		print("The account doesn't seem to be public.Please follow and try again")	
		exit(1)
	if len(result)==0:
		print("Trying to be a smartass are we?")
		print("ERROR:COULDNT FIND ID ATTRIBUTE ON THE PAGE,CHECK USAGE")
		exit(1)
	#print(str(result))
	start=result[1]
	idnum=""
	i=6
	while(htmldoc[start+i]!="\""):
		idnum+=(htmldoc[start+i])
		i=i+1
	print("The id number of the victim :"+idnum)
	getinitfollowers(idnum)

def main():
	if(len(sys.argv)!=2):
		print("usage main.py www.instagram.com/thotname")
		exit(1)
	if len(session)==0:
		print("You forgot to put in the session variable")
		sys.exit(1)
	initgetrequest()


if __name__=="__main__":
	main()
