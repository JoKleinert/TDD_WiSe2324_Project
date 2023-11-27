from django.shortcuts import render  #, redirect
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from datetime import date
import json 
from django.shortcuts import redirect			#redirect is wichtig!
from django.conf import settings
#from django.contrib.auth.models import User		#DjangoAuthentificationSystem

# Create your views here.
def zeitbuchung(request):
	return render(request, "SE3/ZeitbuchungenTest.csv", content_type="text/csv")

def login(request):
	#REGISTRATION
	if request.method== "POST":
		varNeuUser = request.POST.get("userNew", "")
		varNeuPW = request.POST.get("passwordNew", "")
		varNewData = {
			"USER" : varNeuUser,
			"PASSWORD" : varNeuPW
		}
		with open("/var/www/html/login_data.txt", "r") as datei:
			fileRead = json.loads(datei.read())
			if varNeuUser != "" and varNeuPW != "":
				fileRead.append(varNewData)
				# user = User.objects.create_user(varNeuUser, varNeuPW)
				# user.save()
		with open("/var/www/html/login_data.txt", "w") as datei:
			datei.write(json.dumps(fileRead))
	#LOGIN
	if request.method== "POST":
		varLoginUser = request.POST.get("user","")
		varLoginPW = request.POST.get("password", "")
		varCheckData = {
			"USER" : varLoginUser,
			"PASSWORD" : varLoginPW
		}

		with open("/var/www/html/login_data.txt", "r") as datei:
			fileRead = json.loads(datei.read())
			for entry in fileRead:
				if entry == varCheckData:
					return redirect(main)
	#	#	TEST COOKIES	#	#	
	if entry == varCheckData:
		response = HttpResponse("Login successful!")
		response.set_cookie('username', varLoginUser)  # Set a cookie named 'username' with the value varLoginUser
		return response

				
	return render(request, "SE3/ZE_login.html")
def main(request):
	value= request.COOKIES.get('username')
	if value is None:
		return HttpResponse("NEIN DU BIST NICHT REGISTRIERT")
	else:
		return render(request, "SE3/ZE_main.html")  # + {"liste" : dieDateiderDatenmitEinträgen}

def getBaseDir(request):
	return HttpResponse(str(settings.BASE_DIR))

#	#	#	TEST MIT COOKIES	#	#	#
 
def SetCookie(request):
    response = HttpResponse('Visiting for the first time')
    response.set_cookie('bookname','Sherlock Holmes')
    return response
 
def GetCookie(request):
    bookname = request.COOKIES['bookname']
    return HttpResponse(f'The book name is: {bookname}')