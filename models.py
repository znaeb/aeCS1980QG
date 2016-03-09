#import datetime
import logging
import os
import webapp2
#import json
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import memcache


class global_id(ndb.Model):
    next_id = ndb.IntegerProperty()

    def increase_id(self):
        self.next_id = self.next_id + 1

class user_profile(ndb.Model):
    user_id = ndb.StringProperty()
    name = ndb.StringProperty(default="No Name")
    location = ndb.StringProperty(default="No Class")
    interests = ndb.StringProperty(default="No Interests")
    image_url = ndb.StringProperty()
    score = ndb.IntegerProperty(default=0) #maybe have a score variable for each category

class question_obj(ndb.Model):
    id = ndb.StringProperty()
    class_ = ndb.StringProperty()
    question = ndb.StringProperty()
    answer1 = ndb.StringProperty()
    answer2 = ndb.StringProperty()
    answer3 = ndb.StringProperty()
    answer4 = ndb.StringProperty()
    answerid = ndb.StringProperty()
    creator = ndb.StringProperty(default="user")
    correctAnswers = ndb.IntegerProperty(default=0)
    incorrectAnswers = ndb.IntegerProperty(default=0)
    answer1Selections = ndb.IntegerProperty(default=0)
    answer2Selections = ndb.IntegerProperty(default=0)
    answer3Selections = ndb.IntegerProperty(default=0)
    answer4Selections = ndb.IntegerProperty(default=0)
    explanation = ndb.StringProperty(default="No Explantion Provided")
    create_datetime = ndb.DateTimeProperty(auto_now_add=True)
    accepted = ndb.BooleanProperty(default=False)
    up_voters = ndb.StringProperty(repeated=True)
    down_voters = ndb.StringProperty(repeated=True)
    score = ndb.IntegerProperty(default=0)


def update_profile(id, name, location, interests):
    profile = get_user_profile(id)
    profile.populate(name = name, location = location, interests = interests)
    profile.put()
    memcache.set(id, profile, namespace="profile")

def create_profile(id):
    profile = user_profile()
    profile.user_id = id
    profile.key = ndb.Key(user_profile,id)
    profile.put()

    memcache.set(id, profile, namespace="profile")

def check_if_user_profile_exists(id):
    result = list()
    q = user_profile.query(user_profile.user_id == id)
    q = q.fetch(1)
    return q

def get_user_profile(id):
    result = memcache.get(id, namespace="profile")
    if not result:
        result = ndb.Key(user_profile, id).get()
        memcache.set(id, result, namespace="profile")
    return result

def get_image(image_id):
  return ndb.Key(urlsafe=image_id).get()

class global_id(ndb.Model):
    next_id = ndb.IntegerProperty()

    def increase_id(self):
        self.next_id = self.next_id + 1

def get_global_id():
    id = memcache.get("number", namespace="global_id")
    if not id:
        id = ndb.Key(global_id, "number").get()
    logging.warning(id)
    value = id.next_id
    id.increase_id()
    id.put()
    memcache.set("number", id, namespace="global_id")
    return str(value)

def create_global_id():
    id = ndb.Key(global_id, "number").get()
    logging.warning(id)
    if id == None:
        id = global_id()
        id.next_id = 1
        id.key = ndb.Key(global_id, "number")
        id.put()
        memcache.set("number", id, namespace="global_id")

#param: 8(String) question properties
#return: (String) question_number of stored question
#creates and stores question in database
def create_question(category,question,answer1,answer2,answer3,answer4,answerid,explanation,creator,valid):
    question_number = get_global_id()
    question = question_obj(id=question_number,
        class_=category,
        question=question,
        answer1=answer1,
        answer2=answer2,
        answer3=answer3,
        answer4=answer4,
        answerid=answerid,
        explanation=explanation,
        creator=creator,
        accepted=valid)
    question.key = ndb.Key(question_obj, question_number)
    question.put()

    return question_number

#param: (String) id for a query
#return: (question) object
def getQuestion(id):
    ac_obj = ndb.Key(question_obj,id).get()
    return ac_obj

#increments the vote counter
def addVote(id,email):
    question = ndb.Key(question_obj,id).get()

    if not check_if_up_voted(question.up_voters, email):
        question.up_voters.append(email)
        if check_if_down_voted(question.down_voters, email):
            question.down_voters.remove(email)

        question.score = len(question.up_voters) - len(question.down_voters)
        if question.score < 0:
            question.score = 0
        question.put()
        
def check_if_up_voted(has_up_voted,email):
	if email in has_up_voted:
		return True
	return False

def decVote(id,email):    
    question = ndb.Key(question_obj,id).get()
    
    if not check_if_down_voted(question.down_voters, email):
        question.down_voters.append(email)
        if check_if_up_voted(question.up_voters, email):
            question.up_voters.remove(email)

        question.score = len(question.up_voters) - len(question.down_voters)
        if question.score < 0:
            question.score = 0
        question.put()
        
def check_if_down_voted(has_down_voted, email):
	if email in has_down_voted:
		return True
	return False
    
#param: (int) num of requested questions
#return: (list) of questions, oldest first
def get_oldest_questions(num,val):
    if val: #searches for valid questions for reviewal
        query= question_obj.query(question_obj.accepted == True)
        query.order(question_obj.create_datetime)
    else: #search for invalid questions
        query= question_obj.query(question_obj.accepted == False)
        query.order(question_obj.create_datetime)

    return query.fetch(num)

#fills database with question_objs from questions.txt
def populate_db():
    txt = open('questions.txt')
    list = []

    for line in txt:
        list.append(line)

    for x in range(0,len(list), 6):
        question = list[x]
        answer1 = list[x+1]
        answer2 = list[x+2]
        answer3 = list[x+3]
        answer4 = list[x+4]
        answerid = list[x+5]
        create_question("Test", question, answer1, answer2, answer3,
            answer4, answerid,"None","Stephen Curry",True)
