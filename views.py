from django.shortcuts import render  
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from datetime import date
import json 
from django.shortcuts import redirect			#redirect is wichtig!
from django.conf import settings
import csv
import requests
import pwd 			#user account information
import grp
import subprocess
from lxml import etree #pip install in venv 
import signxml
from signxml import XMLSigner, XMLVerifier

#def changeRights(file_path, new_owner):
	# try:
	# 	uid = pwd.getpwnam(new_owner).pw_uid
	# 	gid = os.stat(file_path).st_gid
	# 	os.chown(file_path, uid, gid)
	# except:
	# 	print(f"An error occurred:")
	# try:
	# 	subprocess.run(['sudo', 'chown', '-R', ':www-data', file_path], check=True)
	# 	print(f"Ownership of {file_path} change to www-data.")


# Create your views here.
def login(request):
	errorUser = None
	#REGISTRATION
	if request.method== "POST":	
		action = request.POST.get("ausführen")				#	differenzierung der beiden postmethod 
		if action == "REGISTER":			
			varNeuUser = request.POST.get("userNew", "")
			varNeuPW = request.POST.get("passwordNew", "")
			varNewData = {
				"USER" : varNeuUser,
				"PASSWORD" : varNeuPW,
				"STATUS" : "regular"
			}
			with open("/var/www/html/login_data.txt", "r") as datei:
				fileRead = json.loads(datei.read())
				aktuelleNutzer = set()
				for element in fileRead:
					aktuelleNutzer.add(element["USER"])
				if varNeuUser != "" and varNeuPW != "":					#	absicherung das die andere postmethod nicht genommen wird --> inzwischen nicht mehr nötig?
					if varNeuUser not in aktuelleNutzer:
					# for x in fileRead:
					# 	if x["USER"] == varNeuUser:
					# 		return HttpResponse("Diesen Nutzer gibt es schon")
					# 	else:
						fileRead.append(varNewData)
					else:
						errorUser = "Dieser Nutzername ist bereits vergeben!"
						return render(request, "SE3/ZE_login.html", {"errorUser": errorUser})					
			with open("/var/www/html/login_data.txt", "w") as datei:
				datei.write(json.dumps(fileRead))
			newTextFile = str(varNeuUser) + ".txt"
			if newTextFile == ".txt":					#if varNeuUser == "": --> bei Login wird Registr. Forms trotzdem abgeschickt, aber eben
				pass
			else:
				newFile = "/var/www/html/" + newTextFile
				with open(newFile, "w") as datei:
					datei.write("[]")
				#changeRights(newFile, "ubuntu")
			
		#LOGIN
		# if request.method== "POST":
		if action == "LOGIN":
			varLoginUser = request.POST.get("user","")
			varLoginPW = request.POST.get("password", "")
			varCheckData = {
				"USER" : varLoginUser,
				"PASSWORD" : varLoginPW
			}
			with open("/var/www/html/login_data.txt", "r") as datei:
				fileRead = json.loads(datei.read())
				userGibts = False	
				for entry in fileRead:
					#if entry == varCheckData:
					if entry["USER"] == varLoginUser and entry["PASSWORD"] == varLoginPW:
						status = entry["STATUS"]
						userGibts = True
				if varLoginUser != "":					#vermutlich redundant?
					if userGibts:
						response = redirect(main)
						response.set_cookie("username", varLoginUser)
						response.set_cookie("userStatus", status)
						return response		
					else:
						loginError = "Nutzername oder Password nicht korrekt! Vorsichtig tippen!"
						return render(request, "SE3/ZE_login.html", {"loginError" : loginError})
	return render(request, "SE3/ZE_login.html")

def main(request):
	userCookie = request.COOKIES.get("username")
	userStatus = request.COOKIES.get("userStatus")
	if userCookie is None:
		return HttpResponse("SIE SIND NICHT REGISTRIERT ODER SIE HABEN SICH NICHT ÜBER DIE LOGIN SEITE ANGEMELDET :(")
	else:
		#if request.method== "POST":
		varDate = request.POST.get("date", "")
		varTime = request.POST.get("time", "")
		varModul = request.POST.get("modul", "")
		varBesch = request.POST.get("beschreibung", "")
		varSem = request.POST.get("semester", "")
		
		varEintrag = {
			"date" : varDate,
			"time" : varTime,
			"modul" : varModul,
			"beschreibung" : varBesch,
			"semester" : varSem,
			}
		currentUserFile = "/var/www/html/" + str(userCookie) + ".txt"
		with open(currentUserFile, "r") as fileVorher:
			varVorher = json.loads(fileVorher.read())
			if varDate != "" and varTime != "" and varModul !="" and varBesch !="" and varSem != "":
				varVorher.append(varEintrag)
		with open(currentUserFile, "w") as fileNachher:
			fileNachher.write(json.dumps(varVorher))
		content = {"username" : userCookie, "einträge": varVorher}
		
	
		def zeitenberechnen():
			semesterZeiten = {
			"M1": {"S1": 0, "S2": 0, "S3": 0, "S4": 0, "S5": 0, "S6": 0},
			"M2": {"S1": 0, "S2": 0, "S3": 0, "S4": 0, "S5": 0, "S6": 0},
			"M3": {"S1": 0, "S2": 0, "S3": 0, "S4": 0, "S5": 0, "S6": 0},
			"M4": {"S1": 0, "S2": 0, "S3": 0, "S4": 0, "S5": 0, "S6": 0},
			"M5": {"S1": 0, "S2": 0, "S3": 0, "S4": 0, "S5": 0, "S6": 0},
			"M6": {"S1": 0, "S2": 0, "S3": 0, "S4": 0, "S5": 0, "S6": 0},
			"M7": {"S1": 0, "S2": 0, "S3": 0, "S4": 0, "S5": 0, "S6": 0},
			}
			for eintrag in varVorher:
				modul = eintrag["modul"]
				semester = eintrag["semester"]
				zeit = int(eintrag["time"])
				semesterZeiten[modul][semester] += zeit
			content["semesterZeiten"] = semesterZeiten
			gesamtZeiten = {}
			semesterGesamt = {}
			# Modulzeiten
			for x in semesterZeiten:
				a = 0
				for y in semesterZeiten[x]:
					a += semesterZeiten[x][y]
				gesamtZeiten[x] = a
			# Semesterzeiten
			b1 = 0
			b2 = 0
			b3 = 0
			b4 = 0
			b5 = 0
			b6 = 0
			for x in semesterZeiten:
				for y in semesterZeiten[x]:
					#if semesterZeiten[y] == "S1":
					if y == "S1":
						b1 += semesterZeiten[x][y]
					elif y == "S2":
						b2 += semesterZeiten[x][y]
					elif y == "S3":
						b3 += semesterZeiten[x][y]
					elif y == "S4":
						b4 += semesterZeiten[x][y]
					elif y == "S5":
						b5 += semesterZeiten[x][y]
					elif y == "S6":
						b6 += semesterZeiten[x][y]
				semesterGesamt["S1"] = b1
				semesterGesamt["S2"] = b2
				semesterGesamt["S3"] = b3
				semesterGesamt["S4"] = b4
				semesterGesamt["S5"] = b5
				semesterGesamt["S6"] = b6
			gesamtGesamt = 0
			for x in gesamtZeiten:
				gesamtGesamt += gesamtZeiten[x]
			content["gesamtZeiten"] = gesamtZeiten
			content["semesterGesamt"] = semesterGesamt
			content["gesamtGesamt"] = gesamtGesamt
		zeitenberechnen()
		if request.method == "POST":
			action = request.POST.get("ausführen")
			if action == "upload":
				if 'myfile' in request.FILES:
					myfile = request.FILES["myfile"]
					fileName = str(userCookie) + ".txt"
					fs = FileSystemStorage(location="/var/www/html")
					if fs.exists(fileName):
						fs.delete(fileName)
					filename = fs.save(fileName, myfile)
					with fs.open(fileName) as uploadedFile:
						uploadedContent = uploadedFile.read().decode("utf-8")
					varVorher = json.loads(uploadedContent)
					content["einträge"] = varVorher
					return render(request, "SE3/ZE_main.html", content)
				else:
					return HttpResponse("Ups, da ist was schiefgegangen")
			# elif action == "edit":
			# 	pass
			elif action == "download":
				dateiPfad = "/var/www/html/" + str(userCookie) + ".txt"
				fileName = str(userCookie) + ".json"
				with open(dateiPfad, "rb") as file1:
					malwasanders = HttpResponse(file1.read(), content_type="text/plain")
					malwasanders['Content-Disposition'] = f'attachment; filename="{fileName}"'
					return malwasanders
			elif action == "downloadCSV":
				dateiPfad = "/var/www/html/" + str(userCookie) + ".txt"
				fileName = str(userCookie) + ".csv"
				with open(dateiPfad, "r") as baseFile:
					jsonLoad = json.load(baseFile)
				neuPfad = "var/www/html/" + str(userCookie) + ".csv"
				with open(neuPfad, "w", encoding="utf-8", newline="") as csvDatei:
					#eingelesen = csv.writer(csvDatei, delimiter=",")
					eingelesen = csv.writer(csvDatei, delimiter=",", quotechar='"', quoting=csv.QUOTE_NONNUMERIC) # umgeht non-ASCII characters error
					kopfzeile = []
					for eintrag in jsonLoad[0]:
						kopfzeile.append(eintrag)
					eingelesen.writerow(kopfzeile)
					for dict in jsonLoad:
						zeile = []
						for key in dict:
							werte = dict[key]
							zeile.append(werte)
						eingelesen.writerow(zeile)
				with open (neuPfad, "rb") as ausgangsDatei:
					nochmalWasAnders = HttpResponse(ausgangsDatei.read(), content_type="text/plain")
					nochmalWasAnders['Content-Disposition'] = f'attachment; filename="{fileName}"'
					return nochmalWasAnders
			elif action == "downloadXML":
				dateiPfad = "/var/www/html/" + str(userCookie) + ".txt"
				fileName = str(userCookie) + ".xml"
				with open(dateiPfad, "r") as baseFile:
					jsonLoad = json.load(baseFile)
				neuPfad = "var/www/html/" + str(userCookie) + ".xml"
				with open(neuPfad, "w", encoding="utf-8", newline="") as xmlDatei:
					root = etree.Element("Eintraege")
					for eintrag in jsonLoad:
						subelement = etree.Element("Eintrag")
						subelement.attrib["datum"] = eintrag["date"]
						subelement.attrib["time"] = eintrag["time"]
						subelement.attrib["modul"] = eintrag["modul"]
						subelement.attrib["semester"] = eintrag["semester"]
						subelement.text = eintrag["beschreibung"]
						root.append(subelement)
					gestringed = etree.tostring(root, pretty_print=True).decode("utf-8")
					xmlDatei.write(gestringed)
				with open (neuPfad, "rb") as ausgangsDatei:
					nochmalGanzAnders = HttpResponse(ausgangsDatei.read(), content_type="text/plain")
					nochmalGanzAnders['Content-Disposition'] = f'attachment; filename="{fileName}"'
					return nochmalGanzAnders
			elif action == "downloadUEBER":
				dateiPfad = "/var/www/html/" + str(userCookie) + "Uebersicht" + ".json"
				fileName = str(userCookie) + "Uebersicht.json"
				with open(dateiPfad, "w") as einFile:
					gedumped = json.dumps(content["semesterZeiten"])
					einFile.write(gedumped)
				with open (dateiPfad, "rb") as nochNeDatei:
					könnteEsAuchGleichNennen = HttpResponse(nochNeDatei.read(), content_type="text/plain")
					könnteEsAuchGleichNennen['Content-Disposition'] = f'attachment; filename="{fileName}"'
					return könnteEsAuchGleichNennen
			elif action == "komplettAbmelden":
				userRemove = userCookie
				with open("/var/www/html/login_data.txt", "r") as accountDatei:
					loaded = json.load(accountDatei)
					neueDaten = [user for user in loaded if user.get("USER") != userRemove]
				with open("/var/www/html/login_data.txt", "w") as neuDatei:
					dumped = json.dumps(neueDaten)
					neuDatei.write(dumped)
				with open("/var/www/html/adminRequests.txt", "r") as datei:
					loaded = json.load(datei)
				neueAdminDaten = [user for user in loaded if user != userRemove]
				with open("/var/www/html/adminRequests.txt", "w") as datei:
					gedumped = json.dumps(neueAdminDaten)
					datei.write(gedumped)
				userFile = f"/var/www/html/{userRemove}.txt"
				try:
					os.remove(userFile)
				except:
					pass
				return redirect(login)	
			elif action == "adminAntrag":
				with open("/var/www/html/adminRequests.txt", "r") as datei:
					loaded = json.load(datei)
				if userCookie not in loaded:
					with open("/var/www/html/adminRequests.txt", "w") as datei:
						loaded.append(userCookie)
						gedumped = json.dumps(loaded)
						datei.write(gedumped)
				else:
					pass
			elif action == "adminZulassen":
				user = request.POST.get("user", "")
				with open("/var/www/html/adminRequests.txt", "r") as datei:
					loaded = json.load(datei)
				with open("/var/www/html/adminRequests.txt", "w") as datei:
						loaded.remove(user)
						gedumped = json.dumps(loaded)
						datei.write(gedumped) 
				with open ("/var/www/html/login_data.txt", "r", encoding="utf-8") as jsonDatei:
					loaded = json.loads(jsonDatei.read())
					for x in loaded:
						if x["USER"] == user:
							x["STATUS"] = "admin"

				with open("/var/www/html/login_data.txt", "w") as datei:
					# dumped = json.dumps(loaded)
					# datei.write(dumped)
					json.dump(loaded, datei)
			elif action == "bearbeiten":
				neuNummer = request.POST.get("number", "")
				neuDate = request.POST.get("neudate", "")
				neuTime = request.POST.get("neutime", "")
				neuModul = request.POST.get("neumodul", "")
				neuBesch = request.POST.get("neubeschreibung", "")
				neuSem = request.POST.get("neusemester", "")
				
				neuEintrag = {
					"date" : neuDate,
					"time" : neuTime,
					"modul" : neuModul,
					"beschreibung" : neuBesch,
					"semester" : neuSem,
					}
				currentUserFile = "/var/www/html/" + str(userCookie) + ".txt"
				with open(currentUserFile, "r") as test:
					varVorher = json.loads(test.read())
					nummer = int(neuNummer) - 1
					if 0<= nummer < len(varVorher):
						varVorher[nummer] = neuEintrag
					
				with open(currentUserFile, "w") as test2:
					test2.write(json.dumps(varVorher))
				content["einträge"] = varVorher
				zeitenberechnen()
				return render(request, "SE3/ZE_main.html", content)
			elif action == "löschen":
				löschNummer = request.POST.get("deleteNumber", "")
				with open(currentUserFile, "r") as test3:
					varVorher = json.loads(test3.read())
					nummer = int(löschNummer) - 1
					if 0<= nummer < len(varVorher):
						del varVorher[nummer]
				with open(currentUserFile, "w") as test4:
					test4.write(json.dumps(varVorher))
				content["einträge"] = varVorher
				zeitenberechnen()
				return render(request, "SE3/ZE_main.html", content)


		users=[]
		with open("/var/www/html/login_data.txt", "r") as userDatei:
			geloaded = json.load(userDatei)
			for x in geloaded:
				derName = x["USER"]
				status = x["STATUS"]
				# users[derName] = status
				userData = [derName, status]
				users.append(userData)
		content["userList"] = users
		adminRequests = []
		with open("/var/www/html/adminRequests.txt", "r") as datei:
			loaded = json.load(datei)
			for x in loaded:
				adminRequests.append(x)
		content["adminRequests"] = adminRequests
		content["userStatus"] = userStatus	
		return render(request, "SE3/ZE_main.html", content)
	
def logout(request):
	return render(request, "SE3/ZE_logout.html")










#	#	#	# AB HIER  PROJEKTIRRELEVANTER CODE !!!!!!	#	#	#	
#	#	#	#	#	#	#	#	#	#	#	#	#	#	#	#	#	#	# non-project views	#	#	#	#	#	#	#	#	#	#	#	#	#	#	#	#	#	#	#	#	#	#	
#	#	#	TEST MIT COOKIES	#	#	#
 
# def SetCookie(request):
# 	return HttpResponse("TESTTESTTEST")
#     # response = HttpResponse('Visiting for the first time')
#     # response.set_cookie('bookname','Sherlock Holmes')
#     # return response
 
# def GetCookie(request):
# 	return HttpResponse("TESTTESTTEST")
#     # bookname = request.COOKIES['bookname']
#     # return HttpResponse(f'The book name is: {bookname}')

#	#	#	#	 Zeitbuchung --> Download CSV-file	#	#	#	
def zeitbuchung(request):
	return render(request, "SE3/ZeitbuchungenTest.csv", content_type="text/csv")

#	#	#	GET BASE DIR	#	#	#

def getBaseDir(request):
	return HttpResponse(str(settings.BASE_DIR))

#	#	#	#	#	#	#	#	#	#	#	#ÜBUNGSAUFGABE INF2#	#	#	#	#	#	#	#	#	#	#	#
'''
Aufgabe 1:
Erstellen Sie eine Daten-Quelle mit Mock Daten im Format CSV, die eine Sammlung von Objekten zu Personen enthalten. Unter diesen Daten sollen zumindest E-Mail Adressen und Gender sein.
Stellen Sie die Daten-Quelle auf Ihrem Server online
Erstellen Sie ein Endpoint, welches diese Datenquelle einließt und eine JSON Response liefert, welche folgende Information enthält:
Wie viele Personen verwenden welchen e-Mail Provider (prozentuell)?
Welcher e-Mail Provider ist am beliebtesten je nach Gender?
[{emailprovider:{provider 1: 20%}, {provider2} : 5%}, beliebtester nach gender: {male : provider2}, {female : provider1}]
Aufgabe 2:
Erweitern Sie den Endpoint aus Aufgabe 1 so, dass durch übergebenen URL-Parameter bestimmt werden kann, ob das Response ... enthält: 
a) nur die Info zu der prozentuellen Verteilung der e-Mail Provider
b) nur die Info zu den beliebtesten e-Mail Providern pro Gender
c) beide Infos'''
def personenTest(request):
	class Eintrag:
			alleObjekteNachGender = {}
			def __init__(self, mail, gender):
				self.mail = mail
				self.gender = gender
				if self.gender not in Eintrag.alleObjekteNachGender:
					Eintrag.alleObjekteNachGender[self.gender] = [self]
				else:
					Eintrag.alleObjekteNachGender[self.gender].append(self)
	with open("/var/www/django-project/SE3/templates/SE3/Personen_Test.csv", "r", encoding="utf-8") as datei:
		csvLeser = csv.reader(datei)
		header = next(csvLeser)
		#Aufgabe 1 Teil 1:
		providerAnzahlGesamt = 0
		providerEinzelAnzahl = dict()
		for row in csvLeser:
			Eintrag(row[3], row[4]) 
			mail = row[3]
			gesplittet = mail.split("@")
			mailProvider = gesplittet[1]
			if mailProvider not in providerEinzelAnzahl:
				providerEinzelAnzahl[mailProvider] = 1
			else:
				providerEinzelAnzahl[mailProvider] += 1
			providerAnzahlGesamt += 1
		inProzenten = dict()
		for eintrag in providerEinzelAnzahl:
				value = providerEinzelAnzahl[eintrag]
				prozent = (value * 100) / providerAnzahlGesamt
				inProzenten[eintrag] = prozent
		prozentJson = json.dumps(inProzenten)
		#Aufgabe 1 Teil 2:
		# class Eintrag:
		# 	alleObjekteNachGender = {}
		# 	def __init__(self, mail, gender):
		# 		self.mail = mail
		# 		self.gender = gender
		# 		if gender in Eintrag.alleObjekteNachGender:
		# 			Eintrag.alleObjekteNachGender[gender] = list(self)
		# 		else:
		# 			Eintrag.alleObjekteNachGender[gender].append(self)
		# for row in csvLeser:
		# 	Eintrag(row[5], row[6]) 				----------> MUSS BEIM ERSTEN DURCHITERIEREN PASSIEREN for x in x --> wenn durch, bleibt die Datei quasi hinter der letzten Zeile --> keine Zeilen mehr da
		ausleseDict = {}
		for key in Eintrag.alleObjekteNachGender:
			nextDict = dict()
			ausleseDict[key] = nextDict
			for objekt in Eintrag.alleObjekteNachGender[key]:
				mail = objekt.mail
				gesplittet = mail.split("@")
				provider = gesplittet[1]
				if provider not in ausleseDict[key]:
					nextDict[provider] = 1
				else:
					nextDict[provider] +=1
					
		gedumped = json.dumps(ausleseDict)
	with open("/var/www/django-project/SE3/templates/SE3/TestDict.json", "w", encoding="utf-8") as datei2:
		#gedumped = json.dumps(ausleseDict)
		datei2.write(gedumped)
#--> + ncoh Auswertung welcher Provider am beliebtesten pro Gender ist & Ausgabe in json mit Antwort auf beide Fragen
	return HttpResponse("SCHAUMAL")
#	#	#	#	#	#	#	#	#	#	#	# ENDE ÜBUNG INF2	#	#	#	#	#	#	#	#	#	#	#	#
#	#	# ÜBUNG INF2 XML-Signaturen #	#	#
# Übung: erstellen Sie eine Web-Applikation, 
# mit welcher beliebige XML-Dateien hochgeladen werden können, 
# welche anschließend von der Applikation mit XMLDSig elektronisch signiert werden.

def signieren(request):
	cert = open("/var/www/django-project/SE3/cert.pem").read()
	key = open("/var/www/django-project/SE3/privkey.pem").read()
	if request.method == "POST":
		if 'myfile' in request.FILES:
			myfile = request.FILES["myfile"]
			filename = "testXML.xml"
			fs = FileSystemStorage(location="/var/www/html")
			if fs.exists(filename):
				fs.delete(filename)
			filename = fs.save(filename, myfile)
			with fs.open(filename) as uploadedfile:
				uploadedcontent = uploadedfile.read()
				einXML = etree.fromstring(uploadedcontent)
			with open("/var/www/html/ausgangsXML.xml", "wb") as ausgangsfile:
				signed_root = XMLSigner().sign(einXML, key=key, cert=cert)
				verification_result = XMLVerifier().verify(signed_root, x509_cert=cert)
				pretty = etree.tostring(signed_root, pretty_print=True, encoding="utf-8")
				ausgangsfile.write(pretty)
			with open("/var/www/html/ausgangsXML.xml", "rb") as downDatei:
				könnteEsAuchGleichNennen = HttpResponse(downDatei.read(), content_type="text/plain")
				könnteEsAuchGleichNennen['Content-Disposition'] = f'attachment; filename="bitteschön.xml"'
				return könnteEsAuchGleichNennen


	return render(request, "SE3/signieren.html")