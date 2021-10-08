from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import Usersignupform
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
import requests
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from ratelimit.decorators import ratelimit
from http import HTTPStatus
# Create your views here.
CACHE_TTL = getattr(settings ,'CACHE_TTL' , DEFAULT_TIMEOUT)

def home(request):
	if request.user.is_authenticated:
		return redirect('listing')
	else:
		form = Usersignupform() 
		if request.method=="POST":
			form = Usersignupform(request.POST)
			if form.is_valid():
				form.save()
				username = form.cleaned_data['username']
				password = form.cleaned_data['password1']
			

				user = authenticate(username=username, password=password)
				messages.info(request,"Data Submitted Successfully")
				if user is not None:
					login(request, user)
					return redirect("/listing")
		
		return render(request,'index.html',{'form':form})


def login_request(request):
	if request.user.is_authenticated:
		
		return redirect('listing')
	else:
		if request.method == "POST":
			form = AuthenticationForm(request, data=request.POST)
			if form.is_valid():
				username = form.cleaned_data['username']
				password = form.cleaned_data['password']
			
				user = authenticate(username=username, password=password)
				
				if user is not None:
					login(request, user)
					#messages.info(request, f"You are now logged in as {username}.")
					return redirect("/listing")
				else:
					messages.error(request,"Invalid username or password.")
			else:
				messages.error(request,"Invalid username or password.")
		form = Usersignupform()
		return render(request,'index.html', context={"form":form})



#@ratelimit(key='user_or_ip', rate='1/10m', method=['GET'])
@ratelimit(key='user', rate='100/1d')
@ratelimit(key='user', rate='5/1m')
def listing(request):
	was_limited = getattr(request, 'limited', False)
	if was_limited:
		return HttpResponse('You can search only 5 times in a minute and 100 times in a day.Please try after some time!!!')
		# print(HTTPStatus.BAD_REQUEST,"&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
	else:
		if request.user.is_authenticated:
			data =[]
			if request.method=="GET":
				a = []
				q = ''
				tagged = ''
				nottagged = ''
				accepted = ''
				answers = ''
				q_val =''
				tagged_val=''
				nottagged_val=''
				accepted_val=''
				answers_val=''

				query = request.GET.getlist('keys[]')
				value = request.GET.getlist('value[]')
				page_number = request.GET.get('page')
				if page_number:
					pass
				else:
					page_number = 1
				string_val = ''
				for i,j in  zip(query,value):
					if i=="q":
						q = "&"+i
						q_val = j
					elif i=="tagged":
						tagged = "&"+i
						tagged_val = j
					elif i=="nottagged":
						nottagged = "&"+i
						nottagged_val = j
					elif i=="accepted":
						accepted = "&"+i
						accepted_val = j
					elif i=="answers":
						answers = "&"+i
						answers_val = j
					string_val = string_val+q+"_"+q_val+tagged+"_"+tagged_val+nottagged+"_"+nottagged_val+accepted+"_"+accepted_val+"_"+answers+answers_val
					
				params = {
							'q': q_val,
							'tagged': tagged_val,
							'nottagged': nottagged_val,
							'accepted': accepted_val,
							'answers': answers_val,
							'page' :page_number
						}
				if cache.get(string_val):
					print("DATA COMING FROM CACHE")
					data = cache.get(string_val)
					data = data.json()['items']
					p = Paginator(data,5)
					
					# for i in data:
					# 	print(i)
				else:
					if q_val!='' or tagged_val!='' or nottagged_val!='' or accepted_val!='' or answers_val!='':
						data = requests.get("https://api.stackexchange.com/2.3/search/advanced?site=stackoverflow",params=params)
						cache.set(string_val, data)
						data = data.json()['items']
						print("dataa",data)
						p = Paginator(data,5)
					else:
						data = requests.get("https://api.stackexchange.com/2.3/search/advanced?site=stackoverflow")
						cache.set(string_val, data)
						data = data.json()['items']
						p = Paginator(data,5)
						
						

				
				# listofobjects = [classthing(s) for s in data]
				
				
				try:
					page_obj = p.get_page(page_number)  # returns the desired page object
				except PageNotAnInteger:
					# if page_number is not an integer then assign the first page
					page_obj = p.page(1)
				except EmptyPage:
					# if page is empty then return last page
					page_obj = p.page(p.num_pages)
				context = {'page_obj': page_obj}
				return render(request,'listing.html',{'data':data,"page_obj":page_obj})
			return render(request,'listing.html',{'data':data})
		else:
			return redirect("login")


	
def logout_view(request):
	logout(request)
	messages.info(request,"Logout Successfully")
	return redirect("login")