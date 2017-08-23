from __future__ import unicode_literals
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist
from models import *
import re
import bcrypt
from datetime import date, datetime, timedelta

def index(request):
    return render(request, 'index.html')
def register(request):
    name = request.POST['name']
    alias = request.POST['alias']
    email = request.POST['email']
    password1 = request.POST['password1']
    password2 = request.POST['password2']
    errors = ""
    context = {}
    birthday = request.POST['birthday']
    if not User.objects.isEntered(name, 3):
        errors = errors + " Name must be at least 3 characters and all letters."
    elif not User.objects.isName(name):
        errors = errors + " Name must be at least 3 characters and all letters."
    if not User.objects.isEntered(alias, 3):
        errors = errors + " Alias must be at least 3 characters and all letters."
    elif not User.objects.isName(alias):
        errors = errors + " Alias must be at least 3 characters and all letters."
    if not User.objects.isEntered(email, 5):
        errors = errors + " Email must be entered in a correct format (name@domain.com)."
    elif not User.objects.isEmail(email):
        errors = errors + " Email must be entered in a correct format (name@domain.com)."
    if not User.objects.isEntered(password1, 8):
        errors = errors + " Password must have at least 8 characters"
    if password1 != password2:
        errors = errors + " Password and Verify Password must match"
    if errors == "":
        hash1 = bcrypt.hashpw(password1.encode(), bcrypt.gensalt())
        newuser = User.objects.create(name = name, email_address = email, password= hash1, birthday = birthday, alias = alias)
        context = {}
        context['user'] = newuser
        request.session['loggedinuser'] = newuser.id
        return redirect('pokes/')
    context['errors'] = errors
    return render(request, 'index.html', context)
def login(request):
    email = request.POST['email']
    password1 = request.POST['password']
    errors = ""
    context = {}
    try:
        user1 = User.objects.get(email_address=email)
    except ObjectDoesNotExist:
        context['lerrors'] = "Email address is not associated with a login"
        return render(request, 'index.html', context)
    if not bcrypt.checkpw(password1.encode(), user1.password.encode()):
        context['lerrors'] = "Password is incorrect"
        return render(request, 'index.html', context)
    context['user'] = user1
    request.session['loggedinuser'] = user1.id

    return redirect('/pokes/')

def logout(request):
    del request.session['loggedinuser']
    context = {}
    return redirect('/', context)

def displaypokes(request):
    context = {}
    context['user'] = User.objects.get(id=request.session['loggedinuser'])
    context['userPokedList'] = getUserPokedList(request)
    context['peoplepoked'] = distinctUserPoked(request, request.session['loggedinuser'])
    context['userlist'] = getUserListTable(request)
    return render(request, 'success.html', context)
def pokeotheruser(request):
    user1 = User.objects.get(id=request.session['loggedinuser'])
    pokedid = request.POST['pokeduserid']
    user2 = User.objects.get(id=pokedid)
    context = {}
    Poke.objects.create(poker = user1, poked = user2)
    return redirect('pokes/')

def userlist(request):
    userlist = User.objects.all().exclude(id=request.session['loggedinuser'])
    return userlist

def totalUserPoked(request, userid):
    user = User.objects.get(id=userid)
    total = Poke.objects.all().filter(poked = user).count()
    return total

def distinctUserPoked(request, userid):
    user = User.objects.get(id=userid)
    total = Poke.objects.all().filter(poked = user).values('poker').distinct().count()
    return total

def getUserPokedList(request):
    user = User.objects.get(id=request.session['loggedinuser'])
    pokedList = Poke.objects.all().filter(poked = user).values('poker').annotate(pokecount = Count('poker')).order_by('-pokecount')
    outlist = []
    for line in pokedList:
        # print line['poker']
        user1 = User.objects.get(id=line['poker'])
        outlist.append("{} poked you {} times.".format(user1.alias, line['pokecount']))
    # print outlist
    return outlist
def getUserListTable(request):
    userTableList = []
    allUsers = userlist(request)

    for user in allUsers:
        guy = {}
        guy['id'] = user.id
        guy['name'] = user.name
        guy['alias'] = user.alias
        guy['email'] = user.email_address
        guy['totalpokes'] = "{} pokes".format(totalUserPoked(request, user.id))
        userTableList.append(guy)
        print guy
    return userTableList
