# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.db import connection, IntegrityError, transaction
from datetime import datetime, date
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from dateutil import parser
from base64 import b64encode
from bitarray import bitarray
from django.core.files.base import ContentFile

# Create your views here.
def home(request):
	return render(request, 'homepage/home.html')

@csrf_protect
def login(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect(reverse('home'))
		
	if request.POST:
		cid = request.POST['uname']
		password = request.POST['psw']
		if cid == '':
			return render(request, 'homepage/login.html')
		# print password
		# print make_password(password)
		cursor = connection.cursor()
		cursor.execute("SELECT * from auth_user where username='"+cid+"';")
		data = cursor.fetchone()
		connection.close()

		if data is not None:
			username = data[4]
			# print username, password
			user = auth.authenticate(username=username, password=password)
			if user is not None:
				# print user.is_superuser
				auth.login(request, user)
				messages.success(request, "Login Successful")
				return HttpResponseRedirect(reverse('home'))
			else:
				messages.error(request, 'The username and password combination is incorrect.')
		else:
			messages.error(request, 'ID not registered.')
	return render(request, 'homepage/login.html')


def logout(request):
	if request.user.is_authenticated():
		auth.logout(request)
	return HttpResponseRedirect(reverse('login'))

@csrf_protect
def register(request):
	# print request
	# print request.__dict__
	if request.POST:
		# print type((request.FILES['pic'].read()))
		pic = request.FILES['pic']
		im=pic.read()
		# f=open("xyz.png","w+")
		# f.write(im)
		# for t in pic.__dict__.keys():
		# 	print t, type(pic.__dict__[t])
		# print dir(pic)
		# b=bitarray()
		# b.fromstring(pic)
		# im = b64encode()
		# print p
		# print pic._name
		# return HttpResponse(im, content_type="img/png")
		first_name = request.POST['name']
		last_name = request.POST['surname']
		username = request.POST['uname']
		cursor = connection.cursor()
		cursor.execute("Select username from auth_user;")
		u = cursor.fetchall()
		users = [x[0] for x in u]
		if username in users:
			messages.error(request, 'Username already exists!')
			return HttpResponseRedirect(reverse('register'))
		pass1 = request.POST['pass']
		pass2 = request.POST['passa']
		if pass1!=pass2:
			messages.error(request, "Password do not match!")
			return HttpResponseRedirect(reverse('register'))
		password = make_password(pass1)
		Branch = request.POST['branch']
		if Branch=="#":
			messages.error(request, "Please select branch")
			return HttpResponseRedirect(reverse('register'))
		year = int(request.POST['year'])
		grp = request.POST['group']
		ph = request.POST['phone']
		for c in ph:
			if c not in '0123456789':
				messages.error(request, "Mobile number incorrect!")
				return HttpResponseRedirect(reverse('register'))
		if len(ph)!=10:
			messages.error(request, "Mobile number incorrect!")
			return HttpResponseRedirect(reverse('register'))
		email = request.POST['email']
		cursor.execute("Select Head from Grp where Name='"+grp+"';")
		m = str(cursor.fetchone()[0])
		s = "Insert into auth_user(password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, img) values('"+password+"',0,'"+username+"','"+first_name+"','"+last_name+"','"+email+"',0,1,'"+str(datetime.now())+"', '"+str(im).encode('hex')+"');"
		# print s
		cursor.execute(s)
		cursor.execute("Select max(id) from auth_user;")
		u = str(int(cursor.fetchone()[0]))
		s = "Insert into Student(mID, User, Name, Branch, year, grp, Contact) values("+m+","+u+",'"+first_name+" "+last_name+"','"+Branch+"',"+str(year)+",'"+grp+"','"+ph+"');"
		cursor.execute(s)
		date_time=datetime.now()
		s = "Insert into Notifications(aid,note,date_time) values("+u+", 'Welcome', '"+str(date_time)+"');"
		cursor.execute(s)
		messages.success(request, "Registered")
		return HttpResponseRedirect(reverse('login'))
	return render(request, 'homepage/register.html')

def avatar(request):
	cursor=connection.cursor()
	cursor.execute("Select img from auth_user where id="+str(request.GET.get('id'))+";")
	img = cursor.fetchone()[0].decode('hex')
	return HttpResponse(img, content_type="image/png")

@csrf_protect
def cava(request):
	cursor=connection.cursor()
	if request.POST:
		pic = str(request.FILES['pic'].read()).encode('hex')
		cursor.execute("Update auth_user set img='"+pic+"' where id="+str(request.user.id)+";")
		return HttpResponseRedirect(reverse("dashboard"))
	return render(request, "homepage/ca.html")

def cpg(request):
	flag = False 
	cursor = connection.cursor()
	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, m.Contact, m.User from Grp as g, Mentor as m, auth_user where g.Name='CPG' and g.Head=m.ID and auth_user.is_active=1 and auth_user.id=m.User;")
	head = cursor.fetchone()

	if request.user.is_authenticated():
		if head and request.user.id == head[5]:
			flag=True

	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, m.Contact, m.User from Mentor as m, auth_user where m.grp='CPG' and auth_user.is_active=1 and auth_user.id=m.User and not exists(Select * from Alumni as al where al.mID=m.ID) and not exists(Select * from Admin as ad where ad.mID=m.ID);")
	mentor = cursor.fetchall()

	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, m.Contact, m.User from Mentor as m, auth_user, Alumni as al where m.grp='CPG' and m.ID=al.mID and auth_user.is_active=1 and auth_user.id=m.User;")
	alumni = cursor.fetchall()

	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, ad.Post, m.Contact, m.User from Mentor as m, Admin as ad, auth_user where m.grp='CPG' and m.ID=ad.mID and auth_user.is_active=1 and auth_user.id=m.User;")
	admin = cursor.fetchall()

	cursor.execute("Select s.ID, s.Name, s.Branch, s.Year, m.Name, s.Contact, s.User from Student as s, Mentor as m, auth_user where s.grp='CPG' and m.ID=s.mID and auth_user.is_active=1 and auth_user.id=s.User and s.User<>m.User;")
	student = cursor.fetchall()

	post = ["General Secretary", "Joint Secretary 1", "Joint Secretary 2", "Group Head - CPG", "Group Head - ML", "Group Head - InfoSec", "Group Head - Dev", "Group Head - Finance"]
	connection.close()

	return render(request, 'homepage/cpg.html', {'post': post, 'head': head, 'mentor': mentor, 'admin':admin, 'alumni':alumni, 'student':student, 'flag': flag})

def ml(request):
	flag = False 
	cursor = connection.cursor()
	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, m.Contact, m.User from Grp as g, Mentor as m, auth_user where g.Name='ML' and g.Head=m.ID and auth_user.is_active=1 and auth_user.id=m.User;")
	head = cursor.fetchone()

	if request.user.is_authenticated():
		if head and request.user.id == head[5]:
			flag=True

	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, m.Contact, m.User from Mentor as m, auth_user where m.grp='ML' and auth_user.is_active=1 and auth_user.id=m.User and not exists(Select * from Alumni as al where al.mID=m.ID) and not exists(Select * from Admin as ad where ad.mID=m.ID);")
	mentor = cursor.fetchall()

	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, m.Contact, m.User from Mentor as m, auth_user, Alumni as al where m.grp='ML' and m.ID=al.mID and auth_user.is_active=1 and auth_user.id=m.User;")
	alumni = cursor.fetchall()

	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, ad.Post, m.Contact, m.User from Mentor as m, Admin as ad, auth_user where m.grp='ML' and m.ID=ad.mID and auth_user.is_active=1 and auth_user.id=m.User;")
	admin = cursor.fetchall()

	cursor.execute("Select s.ID, s.Name, s.Branch, s.Year, m.Name, s.Contact, s.User from Student as s, Mentor as m, auth_user where s.grp='ML' and m.ID=s.mID and auth_user.is_active=1 and auth_user.id=s.User and s.User<>m.User;")
	student = cursor.fetchall()

	post = ["General Secretary", "Joint Secretary 1", "Joint Secretary 2", "Group Head - CPG", "Group Head - ML", "Group Head - InfoSec", "Group Head - Dev", "Group Head - Finance"]
	connection.close()

	return render(request, 'homepage/cpg.html', {'post': post, 'head': head, 'mentor': mentor, 'admin':admin, 'alumni':alumni, 'student':student, 'flag': flag})

def fin(request):
	flag = False 
	cursor = connection.cursor()
	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, m.Contact, m.User from Grp as g, Mentor as m, auth_user where g.Name='Finance' and g.Head=m.ID and auth_user.is_active=1 and auth_user.id=m.User;")
	head = cursor.fetchone()

	if request.user.is_authenticated():
		if head and request.user.id == head[5]:
			flag=True

	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, m.Contact, m.User from Mentor as m, auth_user where m.grp='Finance' and auth_user.is_active=1 and auth_user.id=m.User and not exists(Select * from Alumni as al where al.mID=m.ID) and not exists(Select * from Admin as ad where ad.mID=m.ID);")
	mentor = cursor.fetchall()

	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, m.Contact, m.User from Mentor as m, auth_user, Alumni as al where m.grp='Finance' and m.ID=al.mID and auth_user.is_active=1 and auth_user.id=m.User;")
	alumni = cursor.fetchall()

	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, ad.Post, m.Contact, m.User from Mentor as m, Admin as ad, auth_user where m.grp='Finance' and m.ID=ad.mID and auth_user.is_active=1 and auth_user.id=m.User;")
	admin = cursor.fetchall()

	cursor.execute("Select s.ID, s.Name, s.Branch, s.Year, m.Name, s.Contact, s.User from Student as s, Mentor as m, auth_user where s.grp='Finance' and m.ID=s.mID and auth_user.is_active=1 and auth_user.id=s.User and s.User<>m.User;")
	student = cursor.fetchall()

	post = ["General Secretary", "Joint Secretary 1", "Joint Secretary 2", "Group Head - CPG", "Group Head - ML", "Group Head - InfoSec", "Group Head - Dev", "Group Head - Finance"]
	connection.close()

	return render(request, 'homepage/cpg.html', {'post': post, 'head': head, 'mentor': mentor, 'admin':admin, 'alumni':alumni, 'student':student, 'flag': flag})

def infosec(request):
	flag = False 
	cursor = connection.cursor()
	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, m.Contact, m.User from Grp as g, Mentor as m, auth_user where g.Name='InfoSec' and g.Head=m.ID and auth_user.is_active=1 and auth_user.id=m.User;")
	head = cursor.fetchone()

	if request.user.is_authenticated():
		if head and request.user.id == head[5]:
			flag=True

	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, m.Contact, m.User from Mentor as m, auth_user where m.grp='InfoSec' and auth_user.is_active=1 and auth_user.id=m.User and not exists(Select * from Alumni as al where al.mID=m.ID) and not exists(Select * from Admin as ad where ad.mID=m.ID);")
	mentor = cursor.fetchall()

	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, m.Contact, m.User from Mentor as m, auth_user, Alumni as al where m.grp='InfoSec' and m.ID=al.mID and auth_user.is_active=1 and auth_user.id=m.User;")
	alumni = cursor.fetchall()

	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, ad.Post, m.Contact, m.User from Mentor as m, Admin as ad, auth_user where m.grp='InfoSec' and m.ID=ad.mID and auth_user.is_active=1 and auth_user.id=m.User;")
	admin = cursor.fetchall()

	cursor.execute("Select s.ID, s.Name, s.Branch, s.Year, m.Name, s.Contact, s.User from Student as s, Mentor as m, auth_user where s.grp='InfoSec' and m.ID=s.mID and auth_user.is_active=1 and auth_user.id=s.User and s.User<>m.User;")
	student = cursor.fetchall()

	post = ["General Secretary", "Joint Secretary 1", "Joint Secretary 2", "Group Head - CPG", "Group Head - ML", "Group Head - InfoSec", "Group Head - Dev", "Group Head - Finance"]
	connection.close()

	return render(request, 'homepage/cpg.html', {'post': post, 'head': head, 'mentor': mentor, 'admin':admin, 'alumni':alumni, 'student':student, 'flag': flag})

def dev(request):
	lag = False 
	cursor = connection.cursor()
	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, m.Contact, m.User from Grp as g, Mentor as m, auth_user where g.Name='Dev' and g.Head=m.ID and auth_user.is_active=1 and auth_user.id=m.User;")
	head = cursor.fetchone()

	if request.user.is_authenticated():
		if head and request.user.id == head[5]:
			flag=True

	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, m.Contact, m.User from Mentor as m, auth_user where m.grp='Dev' and auth_user.is_active=1 and auth_user.id=m.User and not exists(Select * from Alumni as al where al.mID=m.ID) and not exists(Select * from Admin as ad where ad.mID=m.ID);")
	mentor = cursor.fetchall()

	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, m.Contact, m.User from Mentor as m, auth_user, Alumni as al where m.grp='Dev' and m.ID=al.mID and auth_user.id=m.User;")
	alumni = cursor.fetchall()

	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, ad.Post, m.Contact, m.User from Mentor as m, Admin as ad, auth_user where m.grp='Dev' and m.ID=ad.mID and auth_user.is_active=1 and auth_user.id=m.User;")
	admin = cursor.fetchall()

	cursor.execute("Select s.ID, s.Name, s.Branch, s.Year, m.Name, s.Contact, s.User from Student as s, Mentor as m, auth_user where s.grp='Dev' and m.ID=s.mID and auth_user.is_active=1 and auth_user.id=s.User and s.User<>m.User;")
	student = cursor.fetchall()

	post = ["General Secretary", "Joint Secretary 1", "Joint Secretary 2", "Group Head - CPG", "Group Head - ML", "Group Head - InfoSec", "Group Head - Dev", "Group Head - Finance"]
	connection.close()

	return render(request, 'homepage/cpg.html', {'post': post, 'head': head, 'mentor': mentor, 'admin':admin, 'alumni':alumni, 'student':student, 'flag': flag})


def admin(request):
	cursor = connection.cursor()
	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, m.Contact, m.User from Mentor as m, Admin as ad where m.ID=ad.mID and ad.Post='General Secretary';")
	secy = cursor.fetchone()

	flag=False
	if secy and request.user.id==secy[5]:
		flag=True

	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, m.Contact, m.User from Mentor as m, Admin as ad where m.ID=ad.mID and ad.Post LIKE 'Joint Secretary%';")
	joint = cursor.fetchall()

	cursor.execute("Select m.ID, m.Name, m.Branch, m.Year, m.grp, m.Contact, m.User from Grp as g, Mentor as m where g.Head=m.ID;")
	head = cursor.fetchall()
	connection.close()

	return render(request, 'homepage/admin.html', {'secy': secy, 'j':joint, 'head':head, 'flag':flag})

def merch(request):
	cursor = connection.cursor()
	cursor.execute("Select * from Merchandise;")
	merch = cursor.fetchall()
	final_merch = []
	i=0
	l=[]
	while i< len(merch):
		l.append(merch[i])
		i+=1
		if i%3==0:
			final_merch.append(l)
			l=[]
	if l:
		final_merch.append(l)

	return render(request, 'homepage/merch.html', {'merch': final_merch})

def mavatar(request, ID):
	cursor=connection.cursor()
	cursor.execute("Select design from Merchandise where ID="+str(ID)+";")
	img = cursor.fetchone()[0].decode('hex')
	return HttpResponse(img, content_type="image/png")

@csrf_protect
def sdesigns(request):
	cursor = connection.cursor()
	if request.POST:
		design = str(request.FILES['mpic'].read()).encode('hex')
		name = request.POST['name']
		price = str(request.POST['price'])
		cursor.execute("Insert into Merchandise(design, Price, Designer) values('"+design+"', "+price+", '"+name+"');")
		return HttpResponseRedirect(reverse("merchandise"))
	return render(request, 'homepage/sd.html')

def proj(request):
	cursor = connection.cursor()
	cursor.execute("Select m.ID, m.Name, p.Topic, p.StartDate, m.User from Projects as p, Mentor as m where p.mentor=m.ID and p.Status='Active';")
	active = cursor.fetchall()

	students = []
	for projs in active:
		# print projs[3].strftime('%y-%m-%d')
		# print "Select s.Name from Workers as w, Student as s where w.mentor='"+projs[0]+"' and w.Topic='"+projs[2]+"' and w.StartDate="+projs[3]+" and w.student=s.ID;"
		cursor.execute("Select s.Name, s.ID from Workers as w, Student as s where w.mentor="+str(projs[0])+" and w.Topic='"+projs[2]+"' and w.StartDate='"+str(projs[3])+"' and w.student=s.ID;")
		students.append(cursor.fetchall())

	# collaborations = []
	# for projs in active:
	# 	# print "(select c.mentor1, m.Name, c.Topic1, c.StartDate1 from Collaborations as c, Mentor as m where c.mentor2="+str(projs[0])+" and c.Topic2='"+projs[2]+"' and c.StartDate2='"+str(projs[3])+"' and c.mentor1=m.ID) UNION (select c.mentor2, m.Name, c.Topic2, c.StartDate2 from Collaborations as c, Mentor as m where c.mentor1="+str(projs[0])+" and c.Topic1='"+projs[2]+"' and c.StartDate1='"+str(projs[3])+"' and c.mentor2=m.ID);"
	# 	cursor.execute("(select c.mentor1, m.Name, c.Topic1, c.StartDate1, c.status from Collaborations as c, Mentor as m where c.mentor2="+str(projs[0])+" and c.Topic2='"+projs[2]+"' and c.StartDate2='"+str(projs[3])+"' and c.mentor1=m.ID) UNION (select c.mentor2, m.Name, c.Topic2, c.StartDate2, c.status from Collaborations as c, Mentor as m where c.mentor1="+str(projs[0])+" and c.Topic1='"+projs[2]+"' and c.StartDate1='"+str(projs[3])+"' and c.mentor2=m.ID);")
	# 	collaborations.append(cursor.fetchall())
	connection.close()
	data=[]
	data = [[active[i], students[i]] for i in range(len(active))]
	# print data
	return render(request, 'homepage/projects.html', {'data': data})

def events(request):
	cursor = connection.cursor()
	cursor.execute("Select m.ID, m.Name, e.name, e.date_time, e.type, e.Venue_or_link, m.User from Events as e, Mentor as m where m.ID=e.mentor and e.date_time>='"+str(datetime.now())+"' order by e.date_time;")
	upcoming = cursor.fetchall()
	
	cursor.execute("Select m.ID, m.Name, e.name, e.date_time, e.type, e.Venue_or_link from Events as e, Mentor as m where m.ID=e.mentor and e.date_time<'"+str(datetime.now())+"' order by e.date_time;")
	past = cursor.fetchall()
	
	pstudent = []

	
	for evs in past:
		if evs[4]=="Competition":
			cursor.execute("Select s.Name from Student as s, Participation as p where p.ID=s.ID and p.mentor="+str(evs[0])+" and p.event='"+evs[2]+"' and p.date_time='"+str(evs[3])+"' order by p.status;")
			pstudent.append(cursor.fetchall())
		elif evs[4]=="Workshop":
			pstudent.append([])
	# print pstudent

	p = [[past[i], pstudent[i]] for i in range(len(past))]
	# print p
	return render(request, 'homepage/events.html', {'up':upcoming, 'p':p})

# def sponsors(request):
# 	return HttpResponseRedirect(reverse('home'))
# 	cursor = connection.cursor()
# 	cursor.execute("Select * from Sponsors;")
# 	merch = cursor.fetchall()
# 	final_merch = []
# 	i=0
# 	l=[]
# 	while i< len(merch):
# 		l.append(merch[i])
# 		i+=1
# 		if i%4==0:
# 			final_merch.append(l)
# 			l=[]
# 	if l:
# 		final_merch.append(l)

# 	return render(request, 'homepage/spons.html', {'merch': final_merch})

def notifs(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('login'))
	cursor=connection.cursor()
	cursor.execute("Select note from Notifications where aid="+str(request.user.id)+" and status='unread' order by date_time desc;")
	unread = cursor.fetchall()
	cursor.execute("Select note from Notifications where aid="+str(request.user.id)+" and status='read' order by date_time desc;")
	read = cursor.fetchall()
	# print read
	cursor.execute("Update Notifications set status='read' where aid="+str(request.user.id)+";")
	return render(request, 'homepage/notifs.html', {'unread': unread, 'read': read})

def dashboard(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('login'))
	cursor=connection.cursor()
	cursor.execute("Select * from auth_user where id="+str(request.user.id)+";")
	u=list(cursor.fetchone())
	if u[3]:
		cursor.execute("Select m.ID, m.Name, m.Branch, m.year, ad.Post, m.grp, m.Contact, NULL, m.User from Mentor as m, Admin as ad where m.ID=ad.mID and m.User="+str(u[0])+";")
	elif u[8]:
		cursor.execute("Select m.ID, m.Name, m.Branch, m.year, 'Mentor', m.grp, m.Contact, NULL, m.User from Mentor as m where m.User="+str(u[0])+" and not exists(Select * from Alumni as a where a.mID=m.ID);")
	else:
		cursor.execute("Select s.ID, s.Name, s.Branch, s.year, 'Student', s.grp, s.Contact, m.Name, m.User from Student as s, Mentor as m where m.ID=s.mID and s.User="+str(u[0])+";")
	data = cursor.fetchone()
	if u[8] and not data:
		cursor.execute("Select m.ID, m.Name, m.Branch, m.year, 'Alumni', m.grp, m.Contact, NULL, m.User from Mentor as m, Alumni as a where m.User="+str(u[0])+";")
		data = cursor.fetchone()

	if request.GET:
		# print request.POST['pic']
		name = request.GET.get('name')
		# print name
		# last_name = request.POST['surname']
		username = request.GET.get('username')
		# print username
		cursor = connection.cursor()
		cursor.execute("Select username from auth_user;")
		ux = cursor.fetchall()
		users = [x[0] for x in ux]
		if username in users:
			messages.error(request, 'Username already exists!')
			return HttpResponseRedirect(reverse('dashboard'))
		# pass1 = make_password(request.POST['pass'])
		# pass2 = make_password(request.POST['passa'])
		# if pass1!=pass2:
		# 	messages.error(request, "Password do not match!")
		# 	return render(request, 'homepage/register.html')
		# password = pass1
		grp = request.GET.get('grp')
		# print grp
		if grp not in ['CPG', 'ML', 'Dev', 'InfoSec', 'Fin']:
			messages.error(request, "Wrong Group")
			return HttpResponseRedirect(reverse('dashboard'))
		year = int(request.GET.get('year'))
		Branch = request.GET.get('branch')
		ph = request.GET.get('ph')
		for c in ph:
			if c not in '0123456789':
				messages.error(request, "Mobile number incorrect!")
				return HttpResponseRedirect(reverse('dashboard'))
		if len(ph)!=10:
			messages.error(request, "Mobile number incorrect!")
			return HttpResponseRedirect(reverse('dashboard'))
		email = request.GET.get('email')

		s = "update auth_user set username='"+username+"', email='"+email+"' where id="+str(u[0])+";"
		# print s
		cursor.execute(s)
		# print "b"
		post = request.GET.get('post')
		data=(data[0], name, Branch, year, post, grp, ph, data[7])
		u[7]=email
		u[4]=username
		# print username
		if post=="Student":
			s = "update Student set Name='"+name+"', Branch='"+Branch+"', year="+str(year)+", grp='"+grp+"', Contact='"+ph+"' where User="+str(u[0])+";"
		else:
			s = "update Mentor set Name='"+name+"', Branch='"+Branch+"', year="+str(year)+", grp='"+grp+"', Contact='"+ph+"' where User="+str(u[0])+";"
		cursor.execute(s)
		date_time = datetime.now()
		s = "Insert into Notifications(aid,note,date_time) values("+str(u[0])+", 'Your data is updated', '"+str(date_time)+"');"
		cursor.execute(s)
		return HttpResponseRedirect(reverse('dashboard'))
	return render(request, 'homepage/dash.html', {'data': data, 'last_login':u[2], 'username':u[4], 'email':u[7], 'date_joined':u[10]})


def deactivate(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('login'))
	# print not request.user.is_superuser
	# print request.GET.get('id')!=request.user.id
	# print (not request.user.is_superuser) or request.GET.get('id')!=request.user.id
	# if (not request.user.is_superuser) or ((not request.user.is_superuser) and request.GET.get('id')!=request.user.id):
	# 	messages.error(request, "Can't!")
	# 	return HttpResponseRedirect(reverse('home'))
	if request.GET.get('id')==request.user.id:
		if request.user.is_superuser:
			messages.error(request, "Replace yourself first")
			return HttpResponseRedirect(reverse('home'))
		auth.logout('request')
	cursor = connection.cursor()
	cursor.execute("Select is_superuser, is_staff from auth_user where id="+str(request.GET.get('id'))+";")
	isu = cursor.fetchone()
	if request.user.is_superuser:
		if isu[0]:
			messages.error(request, "Replace first")
			return HttpResponseRedirect(reverse('home'))
	cursor.execute("Update auth_user set is_active=0 where id="+str(request.GET.get('id'))+";")
	date_time=datetime.now()
	cursor.execute("Insert into Notifications(aid,note,date_time) values("+str(request.GET.get('id'))+", 'Your account was deactivated', '"+str(date_time)+"');")
	if isu[1]:
		cursor.execute("Select ID, Name from Mentor where User="+str(request.GET.get('id'))+";")
		men = cursor.fetchone()
		mid = men[0]
		name = men[1]
		cursor.execute("Insert into Alumni(mID, Name) values("+str(mid)+", "+name+");")
	return HttpResponseRedirect(reverse('admin'))

def madmin(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('login'))
	if not request.user.is_superuser:
		messages.error(request, "Can't!")
		return HttpResponseRedirect(reverse('home'))
	new_id = request.GET.get("id")
	post = request.GET.get("post")
	s = "Select a.mID, m.User, m.Name from Admin as a, Mentor as m where a.Post='"+post+"' and a.mID=m.ID;"
	cursor=connection.cursor()
	cursor.execute(s)
	old = cursor.fetchone()
	old_id=0
	old_mid=0
	old_name="null"
	if old:
		old_id = old[1]
		old_mid = old[0]
		old_name = old[2]
	# print new_id
	s = "Select ID, Name from Mentor where User="+str(new_id)+";"
	cursor.execute(s)
	new = cursor.fetchone()
	s = "Delete from Admin where Post='"+post+"';"
	cursor.execute(s)
	# print "Insert into Admin values("+str(new[0])+", '"+new[1]+"', '"+post+"');"
	s = "Insert into Admin values("+str(new[0])+", '"+new[1]+"', '"+post+"');"
	cursor.execute(s)
	if old:
		s = "Select * from Admin where mID="+str(old_mid)+";"
		cursor.execute(s)
		flag = cursor.fetchone()
		if flag:
			pass
		else:
			s = "Insert into Alumni(mID, Name) values("+str(old_mid)+", '"+old_name+"');"
			cursor.execute(s)
			s = "update auth_user set is_superuser=0 where id="+str(old_id)+";"
			cursor.execute(s)
	if "Group" in post:
		s = "update Grp set Head="+str(new[0])+" where Name='"+post.split("Group Head - ")[1]+"';"
		cursor.execute(s)
	s = "update auth_user set is_superuser=1 where id="+str(new_id)+";"
	cursor.execute(s)
	s="Delete from Alumni where mID="+str(new[0])+";"
	cursor.execute(s)
	date_time=datetime.now()
	s="Insert into Notifications(aid,note,date_time) values("+str(new_id)+", 'Your are now "+post+"', '"+str(date_time)+"');"
	cursor.execute(s)
	if old:
		s="Insert into Notifications(aid,note,date_time) values("+str(old_id)+", 'Your are removed from "+post+"', '"+str(date_time)+"');"
		cursor.execute(s)
	connection.close()
	return HttpResponseRedirect(reverse('admin'))

def mmentor(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('login'))
	if not request.user.is_superuser:
		messages.error(request, "Can't!")
		return HttpResponseRedirect(reverse('home'))
	new_id = request.GET.get("id")
	cursor=connection.cursor()
	cursor.execute("Select * from Student where User="+str(new_id)+";")
	st = cursor.fetchone()
	
	cursor.execute("Insert into Mentor(User, Name, Branch, year, grp, Contact) values("+str(st[2])+", '"+str(st[3])+"', '"+str(st[4])+"', "+str(st[5])+", '"+str(st[6])+"', '"+str(st[7])+"');")
	cursor.execute("Select ID from Mentor where User="+str(new_id)+";")
	i = cursor.fetchone()[0]
	cursor.execute("Update Student set mID="+str(i)+" where User="+str(new_id)+";")
	cursor.execute("Update auth_user set is_staff=1 where id="+str(new_id)+";")
	s="Insert into Notifications(aid,note,date_time) values("+str(new_id)+", 'Your are now mentor', '"+str(date_time)+"');"
	cursor.execute(s)
	dic = {'CPG': 'cpg', 'ML': 'ml', 'InfoSec': 'infosec', 'Finance':'fin', 'Dev':'dev'}
	return HttpResponseRedirect(reverse(dic[st[6]]))	

def amentor(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('login'))
	if not request.user.is_superuser:
		messages.error(request, "Can't!")
		return HttpResponseRedirect(reverse('home'))
	cursor=connection.cursor()
	i=request.GET.get('ment')
	new_id=request.GET.get('id')
	cursor.execute("Update Student set mID="+str(i)+" where User="+str(new_id)+";")
	cursor.execute("Select * from Student where User="+str(new_id)+";")
	st = cursor.fetchone()
	date_time=datetime.now()
	s="Insert into Notifications(aid,note,date_time) values("+str(new_id)+", 'Your mentor is changed', '"+str(date_time)+"');"
	cursor.execute(s)
	dic = {'CPG': 'cpg', 'ML': 'ml', 'InfoSec': 'infosec', 'Finance':'fin', 'Dev':'dev'}
	return HttpResponseRedirect(reverse(dic[st[6]]))

def cproj(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('login'))
	if not request.user.is_staff:
		messages.error(request, "Can't!")
		return HttpResponseRedirect(reverse('home'))
	cursor = connection.cursor()
	cursor.execute("Select ID from Mentor where User="+str(request.user.id)+";")
	mentor = cursor.fetchone()[0]
	if request.GET:
		topic = request.GET.get('topic')
		dat = datetime.today()
		desc = request.GET.get('Description')
		# print "Insert into Projects values("+str(mentor)+", '"+topic+"', '"+str(dat)+"', 'active', '"+desc+"');"
		cursor.execute("Insert into Projects values("+str(mentor)+", '"+topic+"', '"+str(dat)+"', 'active', '"+desc+"');")
		date_time=datetime.now()
		s="Insert into Notifications(aid,note,date_time) values("+str(request.user.id)+", 'Your project ~"+topic+"~ is created', '"+str(date_time)+"');"
		cursor.execute(s)
		return HttpResponseRedirect(reverse('projects'))
	return render(request, 'homepage/cp.html')

def dproj(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('login'))
	if not request.user.is_staff:
		messages.error(request, "Can't!")
		return HttpResponseRedirect(reverse('home'))
	cursor = connection.cursor()
	ment = request.GET.get('ment')
	topic = request.GET.get('topic')
	dic = {'Jan.':'01', 'Feb.':'02', 'March':'03', 'April':'04', 'May':'05', 'June':'06', 'July':'07', 'Aug.':'08', 'Sept.':'09', 'Oct.':'10', 'Nov.':'11', 'Dec.':'12'}
	
	dat = str(request.GET.get('dat'))
	date_ = ''
	finald = ''
	i=0
	l=len(dat)
	while i<l:
		if dat[i]==' ':
			break
		date_=date_+dat[i]
		i+=1
	finald=dic[date_]
	date_=''
	i+=1
	while i<l:
		if dat[i]==',':
			i+=1
			break
		date_=date_+dat[i]
		i+=1
	finald=finald+'-'+date_
	date_=''
	i+=1
	while i<l:
		date_=date_+dat[i]
		i+=1
	finald=date_+'-'+finald

	cursor.execute("Delete from Workers where mentor="+str(ment)+" and Topic='"+topic+"' and StartDate='"+finald+"';")
	# print "Delete from Projects where("+str(mentor)+", '"+topic+"', '"+str(dat)+"', 'active', '"+desc+"');"
	cursor.execute("Delete from Projects where mentor="+str(ment)+" and Topic='"+topic+"' and StartDate='"+finald+"';")
	date_time=datetime.now()
	s="Insert into Notifications(aid,note,date_time) values("+str(request.user.id)+", 'Your project ~"+topic+"~ is deleted', '"+str(date_time)+"');"
	cursor.execute(s)
		
	return HttpResponseRedirect(reverse('projects'))
	# return render(request, 'homepage/cp.html')


def devent(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('login'))
	if not request.user.is_staff:
		messages.error(request, "Can't!")
		return HttpResponseRedirect(reverse('home'))
	cursor = connection.cursor()
	ment = request.GET.get('ment')
	topic = request.GET.get('topic')
	dic = {'Jan.':'01', 'Feb.':'02', 'March':'03', 'April':'04', 'May':'05', 'June':'06', 'July':'07', 'Aug.':'08', 'Sept.':'09', 'Oct.':'10', 'Nov.':'11', 'Dec.':'12'}
	
	dat = str(request.GET.get('dat'))
	dat = dat.replace("midnight", "00:00 a.m.")
	dat = dat.replace("noon", "12:00 p.m.")
	dat = parser.parse(dat)

	cursor.execute("Delete from Participation where mentor="+str(ment)+" and event='"+topic+"' and date_time='"+str(dat)+"';")
	# print "Delete from Projects where("+str(mentor)+", '"+topic+"', '"+str(dat)+"', 'active', '"+desc+"');"
	cursor.execute("Delete from Events where mentor="+str(ment)+" and name='"+topic+"' and date_time='"+str(dat)+"';")
	date_time=datetime.now()
	s="Insert into Notifications(aid,note,date_time) values("+str(request.user.id)+", 'Your event ~"+topic+"~ is deleted', '"+str(date_time)+"');"
	cursor.execute(s)
	return HttpResponseRedirect(reverse('events'))


def jproj(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('login'))
	if request.user.is_staff:
		messages.error(request, "Can't! Wanna Collaborate?")
		return HttpResponseRedirect(reverse('home'))
	dic = {'Jan.':'01', 'Feb.':'02', 'March':'03', 'April':'04', 'May':'05', 'June':'06', 'July':'07', 'Aug.':'08', 'Sept.':'09', 'Oct.':'10', 'Nov.':'11', 'Dec.':'12'}
	ment = request.GET.get('ment')
	topic = request.GET.get('topic')
	
	dat = str(request.GET.get('dat'))
	date_ = ''
	finald = ''
	i=0
	l=len(dat)
	while i<l:
		if dat[i]==' ':
			break
		date_=date_+dat[i]
		i+=1
	finald=dic[date_]
	date_=''
	i+=1
	while i<l:
		if dat[i]==',':
			i+=1
			break
		date_=date_+dat[i]
		i+=1
	finald=finald+'-'+date_
	date_=''
	i+=1
	while i<l:
		date_=date_+dat[i]
		i+=1
	finald=date_+'-'+finald

	cursor = connection.cursor()
	cursor.execute("Select ID, Name from Student where User="+str(request.user.id)+";")
	stud = cursor.fetchone()
	cursor.execute("Select User from Mentor where ID="+str(ment)+";")
	mmm = cursor.fetchone()[0]
	# print "Select count(*) from Workers where student="+str(stud[0])+", mentor="+str(ment)+", Topic='"+topic+"', StartDate='"+finald+"';"
	cursor.execute("Select count(*) from Workers where student="+str(stud[0])+" and mentor="+str(ment)+" and Topic='"+topic+"' and StartDate='"+finald+"';")
	x = cursor.fetchone()[0]
	if x==1:
		messages.error(request, "Already in the project")
		return HttpResponseRedirect(reverse('projects'))
	elif x==0:
		cursor.execute("Insert into Workers values("+str(stud[0])+", "+str(ment)+", '"+topic+"', '"+finald+"');")
		date_time=datetime.now()
		s="Insert into Notifications(aid,note,date_time) values("+str(request.user.id)+", 'Your joined project ~"+topic+"~ ', '"+str(date_time)+"');"
		cursor.execute(s)
		# date_time=datetime.now()
		s="Insert into Notifications(aid,note,date_time) values("+str(mmm)+", '"+stud[1]+" joined project ~"+topic+"~ ', '"+str(date_time)+"');"
		cursor.execute(s)
		return HttpResponseRedirect(reverse('projects'))

def cevent(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('login'))
	if not request.user.is_staff:
		messages.error(request, "Can't!")
		return HttpResponseRedirect(reverse('home'))
	cursor = connection.cursor()
	cursor.execute("Select ID from Mentor where User="+str(request.user.id)+";")
	mentor = cursor.fetchone()[0]
	if request.GET:
		name = request.GET.get('topic')
		dat = request.GET.get('dat')
		vl = request.GET.get('vl')
		t = request.GET.get('type')
		# print "Insert into Events values("+str(mentor)+", '"+name+"', '"+str(dat)+"', '"+t+"', '"+vl+"');"
		cursor.execute("Insert into Events values("+str(mentor)+", '"+name+"', '"+str(dat)+"', '"+t+"', '"+vl+"');")
		date_time=datetime.now()
		s="Insert into Notifications(aid,note,date_time) values("+str(request.user.id)+", 'Your event ~"+name+"~ is created', '"+str(date_time)+"');"
		cursor.execute(s)
		return HttpResponseRedirect(reverse('events'))
	return render(request, 'homepage/ce.html')

def jev(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('login'))
	if request.user.is_staff:
		messages.error(request, "Can't! Wanna Collaborate?")
		return HttpResponseRedirect(reverse('home'))
	# dic = {'Jan.':'01', 'Feb.':'02', 'March':'03', 'April':'04', 'May':'05', 'June':'06', 'July':'07', 'Aug.':'08', 'Sept.':'09', 'Oct.':'10', 'Nov.':'11', 'Dec.':'12'}
	ment = request.GET.get('ment')
	topic = request.GET.get('event')
	
	dat = str(request.GET.get('dat'))
	dat = dat.replace("midnight", "00:00 a.m.")
	dat = dat.replace("noon", "12:00 p.m.")
	dat = parser.parse(dat)
	# date_ = ''
	# finald = ''
	# i=0
	# l=len(dat)
	# while i<l:
	# 	if dat[i]==' ':
	# 		break
	# 	date_=date_+dat[i]
	# 	i+=1
	# finald=dic[date_]
	# date_=''
	# i+=1
	# while i<l:
	# 	if dat[i]==',':
	# 		i+=1
	# 		break
	# 	date_=date_+dat[i]
	# 	i+=1
	# finald=finald+'-'+date_
	# date_=''
	# i+=1
	# while i<l:
	# 	date_=date_+dat[i]
	# 	i+=1
	# finald=date_+'-'+finald
	# print str(dat)
	cursor = connection.cursor()
	cursor.execute("Select ID, Name from Student where User="+str(request.user.id)+";")
	stud = cursor.fetchone()
	# print "Select * from Events where mentor="+str(ment)+", name='"+topic+"', date_time='"+str(dat)+"';"
	cursor.execute("Select * from Events where mentor="+str(ment)+" and name='"+topic+"' and date_time='"+str(dat)+"';")
	y=cursor.fetchone()
	flag=False
	if y[3]=="Competition":
		flag=True
	# print "Select count(*) from Participation where ID="+str(stud[0])+" and mentor="+str(ment)+" and event='"+topic+"' and date_time='"+str(dat)+"';"
	cursor.execute("Select User from Mentor where ID="+str(ment)+";")
	mmm = cursor.fetchone()[0]
	cursor.execute("Select count(*) from Participation where ID="+str(stud[0])+" and mentor="+str(ment)+" and event='"+topic+"' and date_time='"+str(dat)+"';")
	x = cursor.fetchone()[0]
	if x==1:
		messages.error(request, "Already registered")
		return HttpResponseRedirect(reverse('events'))
	elif x==0:
		if flag:
			cursor.execute("Select count(*) from Participation where mentor="+str(ment)+" and event='"+topic+"' and date_time='"+str(dat)+"';")
			x = cursor.fetchone()[0]+1
			cursor.execute("Insert into Participation values("+str(stud[0])+", "+str(ment)+", '"+topic+"', '"+str(dat)+"', "+str(x)+");")
		else:
			cursor.execute("Insert into Participation(ID, mentor, event, date_time) values("+str(stud[0])+", "+str(ment)+", '"+topic+"', '"+str(dat)+"');")
		date_time=datetime.now()
		s="Insert into Notifications(aid,note,date_time) values("+str(request.user.id)+", 'Your joined event ~"+topic+"~ ', '"+str(date_time)+"');"
		cursor.execute(s)
		# date_time=datetime.now()
		s="Insert into Notifications(aid,note,date_time) values("+str(mmm)+", '"+stud[1]+" joined project ~"+topic+"~ ', '"+str(date_time)+"');"
		cursor.execute(s)
		return HttpResponseRedirect(reverse('events'))

def order(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('login'))
	cursor = connection.cursor()
	total = 0
	desc = "merch="
	for merch in request.GET.keys():
		cursor.execute("Select * from Merchandise where ID="+str(merch)+";")
		mer = cursor.fetchone()
		total+=int(mer[2])
		desc=desc+str(merch)+","
	cursor.execute("Select username from auth_user where id="+str(request.user.id)+";")
	us = cursor.fetchone()[0]
	desc=desc+"user="+str(us)
	cursor.execute("Insert into TrsnID() values();")
	cursor.execute("Select max(id) from TrsnID;")
	order_id = str(cursor.fetchone()[0])
	return render(request, 'homepage/buy.html', {'total':total, 'desc': desc, 'order_id':order_id})

def call_meeting(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('login'))
	if not request.user.is_superuser:
		messages.error(request, "Can't!")
		return HttpResponseRedirect(reverse('home'))
	aid = request.user.id;
	cursor=connection.cursor()
	cursor.execute("Select count(*) from Mentor as m, Admin as a where m.ID=a.mID and a.Post='General Secretary' and m.User="+str(aid)+";")
	x=cursor.fetchone()[0]
	if x==0:
		messages.error(request, "Can't!")
		return HttpResponseRedirect(reverse('home'))
	if request.GET:
		loc = request.GET.get('v')
		topic = request.GET.get('topic')
	
		dat = str(request.GET.get('dat'))
		dat = dat.replace("midnight", "00:00 a.m.")
		dat = dat.replace("noon", "12:00 p.m.")
		dat = parser.parse(dat)

		cursor.execute("Insert into Meetings(topic, venue, date_time) values('"+topic+"', '"+loc+"', '"+str(dat)+"');")
		cursor.execute("Select id from auth_user where is_superuser=1;")
		date_time=datetime.now()
		x=cursor.fetchall()
		for i in x:
			s="Insert into Notifications(aid,note,date_time) values("+str(i[0])+", 'Meeting scheduled at "+loc+" on "+str(dat)+"', '"+str(date_time)+"');"
			cursor.execute(s)
		cursor.execute("Select max(id) from Meetings;")
		y=cursor.fetchone()[0]
		cursor.execute("Select ID from Mentor where User="+str(request.user.id)+";")
		z=cursor.fetchone()[0]
		cursor.execute("Insert into MeetingAttendees values("+str(y)+", "+str(z)+");")
		return HttpResponseRedirect(reverse('admin'))

	return render(request, 'homepage/cm.html')

def attend_meet(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('login'))
	if not request.user.is_superuser:
		messages.error(request, "Can't!")
		return HttpResponseRedirect(reverse('home'))
	aid = request.user.id;
	cursor=connection.cursor()
	cursor.execute("Select id, topic, venue, date_time from Meetings where date_time>='"+str(datetime.now())+"';")
	data = cursor.fetchall()
	# print data
	cursor.execute("Select ID from Mentor where User="+str(aid)+";")
	y=cursor.fetchone()[0]
	cursor.execute("Select ma.meeting_id, m.Name from Mentor as m, MeetingAttendees as ma where ma.admin_id=m.ID;")
	meets = cursor.fetchall()
	cursor.execute("Select count(*) from Mentor as m, Admin as a where m.ID=a.mID and a.Post='General Secretary' and m.User="+str(aid)+";")
	x=cursor.fetchone()[0]
	flag=False
	if x==1:
		flag=True
	if request.GET:
		for mid in request.GET.keys():
			cursor.execute("Insert into MeetingAttendees values("+str(mid)+", "+str(y)+");")
		return HttpResponseRedirect(reverse('admin'))

	return render(request, 'homepage/am.html', {'data': data, 'meets':meets, 'flag':flag})