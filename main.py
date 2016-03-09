import logging
import os
import webapp2
import models
import time

from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from google.appengine.api import mail

###############################################################################
# We'll just use this convenience function to retrieve and render a template.
def render_template(handler, templatename, templatevalues={}):
  path = os.path.join(os.path.dirname(__file__), 'templates/' + templatename)
  html = template.render(path, templatevalues)
  handler.response.out.write(html)


###############################################################################
def get_user_email():
    result = None
    user = users.get_current_user()
    if user:
        result = user.email()
    return result

def get_user_id():
    result = None
    user = users.get_current_user()
    if user:
        result = user.user_id()
    return result

class MainPageHandler(webapp2.RequestHandler):
    def get(self):
        id = get_user_id()
        is_admin = 0
        if users.is_current_user_admin():
            is_admin = 1
        q = models.check_if_user_profile_exists(id)

        page_params = {
        'user_email': get_user_email(),
        'login_url': users.create_login_url(),
        'logout_url': users.create_logout_url('/'),
        'user_id': id,
        'admin' : is_admin
        }
        render_template(self, 'index.html', page_params)


class SubmitPageHandler(webapp2.RequestHandler):
    def get(self):
        id = get_user_id()
        is_admin = 0
        if users.is_current_user_admin():
            is_admin = 1
        q = models.check_if_user_profile_exists(id)

        page_params = {
        'user_email': get_user_email(),
        'login_url': users.create_login_url(),
        'logout_url': users.create_logout_url('/'),
        'user_id': id,
		'admin' : is_admin
        }
        render_template(self, 'newQuestionSubmit.html', page_params)

class NewQuestion(webapp2.RequestHandler):
    def post(self):
        id = get_user_id()
        q = models.get_user_profile(id)
        creator = q.name
        explanation = self.request.get('explanation')
        if not explanation:
            explanation = "No Explanation Provided"
        category = self.request.get('category')
        question = self.request.get('questiontext')
        answer1 = self.request.get('answer1')
        answer2 = self.request.get('answer2')
        answer3 = self.request.get('answer3')
        answer4 = self.request.get('answer4')
        answerid = self.request.get('answerid')
        questionID = models.create_question(category,question,answer1,answer2,answer3,answer4,answerid,explanation,creator,False)
        self.redirect('/NewQuestion?id=' + questionID)

    def get(self):
        id = self.request.get('id')
        page_params = {
            'questionID' : id
        }
        render_template(self, 'confirmationPage.html', page_params)

class ReviewSingleQuestion(webapp2.RequestHandler):
    def get(self):
        id = self.request.get('id')
        uID = get_user_id()
        review = models.getQuestion(id)
        is_admin = 0
        if users.is_current_user_admin():
            is_admin = 1
        page_params = {
        'user_email': get_user_email(),
        'login_url': users.create_login_url(),
        'logout_url': users.create_logout_url('/'),
        'user_id': uID,
		'review': review,
        'admin' : is_admin
        }
        render_template(self, 'newQuestionReview.html', page_params)

#Brings up a table that displays information on the most recent 1000 questions
class ReviewNewQuestions(webapp2.RequestHandler):
    def get(self):
        uID = get_user_id()
        #just loops and prints every question from query
        review = models.get_oldest_questions(1000,False) #searches 1000 oldest invalid questions
        is_admin = 0
        if users.is_current_user_admin():
            is_admin = 1
        page_params = {
        'user_email': get_user_email(),
        'login_url': users.create_login_url(),
        'logout_url': users.create_logout_url('/'),
        'user_id': uID,
		'review': review,
        'admin' : is_admin
        }
        render_template(self, 'reviewQuestions.html', page_params)

#Brings up a table that displays information on the most recent 1000 questions
class ReviewOldQuestions(webapp2.RequestHandler):
    def get(self):
        uID = get_user_id()
        #just loops and prints every question from query
        review = models.get_oldest_questions(1000,True) #searches 1000 oldest valid questions
        is_admin = 0
        if users.is_current_user_admin():
            is_admin = 1
        page_params = {
        'user_email': get_user_email(),
        'login_url': users.create_login_url(),
        'logout_url': users.create_logout_url('/'),
        'user_id': uID,
		'review': review,
        'admin' : is_admin
        }
        render_template(self, 'reviewQuestionsValid.html', page_params)

class test(webapp2.RequestHandler):
    def get(self):
        models.create_global_id()
        models.populate_db()
        id = get_user_id()
        is_admin = 0
        if users.is_current_user_admin():
            is_admin = 1
        q = models.check_if_user_profile_exists(id)
        page_params = {
        'user_email': get_user_email(),
        'login_url': users.create_login_url(),
        'logout_url': users.create_logout_url('/'),
        'user_id': id,
        'admin' : is_admin
        }
        render_template(self, 'index.html', page_params)

class AnswerQuestion(webapp2.RequestHandler):
    def get(self):
        #answerid = self.request.get('answerid')
        #id = self.request.get('id')
        review = models.get_oldest_questions(1)
        is_admin = 0
        if users.is_current_user_admin():
            is_admin = 1
        page_params = {
          'user_email': get_user_email(),
          'login_url': users.create_login_url(),
          'logout_url': users.create_logout_url('/'),
          'review': review,
		  'admin': is_admin,
        }
        render_template(self, 'answerQuestion.html',page_params)

class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        id = self.request.get("id")
        q = models.check_if_user_profile_exists(id)
        if q == []:
            models.create_profile(id)
        is_admin = 0
        if users.is_current_user_admin():
            is_admin = 1
        page_params = {
            'user_email': get_user_email(),
            'login_url': users.create_login_url(),
            'logout_url': users.create_logout_url('/'),
            'user_id': get_user_id(),
            'profile': models.get_user_profile(id),
			'admin': is_admin,
        }
        render_template(self, 'profile1.html', page_params)

    def post(self):
        id = get_user_id()
        name = self.request.get("name")
        location = self.request.get("location")
        interests = self.request.get("interests")

        models.update_profile(id, name, location, interests)

        self.redirect('/profile?id=' + id + "&search=" + get_user_email())

class submitQuiz(webapp2.RequestHandler):
    def post(self):
        is_admin = 0
        if users.is_current_user_admin():
            is_admin = 1
        page_params = {
          'user_email': get_user_email(),
          'login_url': users.create_login_url(),
          'logout_url': users.create_logout_url('/'),
          'correctCount': numCorrect,
          'totalCount': numTotal,
          'question_obj': argQ,
		  'admin': is_admin,
        }
        render_template(self,'quizResults.html',page_params)

class answerSingle(webapp2.RequestHandler):
    def get(self):
        argQ = models.getQuestion(str(2))
        id = get_user_id()
        numCorrect = 0
        numTotal = 0
        is_admin = 0
        if users.is_current_user_admin():
            is_admin = 1
        page_params = {
          'user_email': get_user_email(),
          'login_url': users.create_login_url(),
          'logout_url': users.create_logout_url('/'),
          'correctCount': numCorrect,
          'totalCount': numTotal,
          'question_obj': argQ,
          'user_id':id,
		  'admin': is_admin,
        }
        render_template(self,'answerSingle.html',page_params)

class submitAnswer(webapp2.RequestHandler):
    def post(self):
        #instead of hiding the answerid can we hide the full data entry for the question
        #this will allow for tracking the answers as well as removing the answer to the question
        #from the page source, or we could store the questionid and query the db, eventhough
        #we want to make queries as infrequent as possible
        #answerid = self.request.get('hidden_answerid')
        id = self.request.get('hidden_questionid')
        question = models.getQuestion(id)
        if not question: #checks to make sure a question was actually fetched
            #maybe redirect here instead of showing an empty question page, error page possibly
            self.redirect('home')
            logging.warning("no question found with that id")
        answerid = question.answerid
        questionid = self.request.get('userAnswer')
        correctCount = self.request.get('hidden_correctCount')
        totalCount = self.request.get('hidden_totalCount')
        answerid = int(answerid)
        questionid = int(questionid)
        correctCount = int(correctCount)
        totalCount = int(totalCount)
        id = get_user_id()
        is_admin = 0
        if users.is_current_user_admin():
            is_admin = 1
        if (questionid == answerid):
            correctCount = correctCount+1
        totalCount = totalCount+1
        if (totalCount == 10):
            page_params = {
              'user_email': get_user_email(),
              'login_url': users.create_login_url(),
              'logout_url': users.create_logout_url('/'),
              'correctCount': correctCount,
              'totalCount': totalCount,
			  'admin': is_admin,
            }
            render_template(self,'quizResults.html',page_params)
            return
        argQ = models.getQuestion(str(2+totalCount))
        page_params = {
          'user_email': get_user_email(),
          'login_url': users.create_login_url(),
          'logout_url': users.create_logout_url('/'),
          'correctCount': correctCount,
          'totalCount': totalCount,
          'question_obj': argQ,
          'user_id':id,
		  'admin': is_admin,
        }
        render_template(self,'answerSingle.html',page_params)

class reportHandler(webapp2.RequestHandler):
    def post(self):
        body = "Comment:\n" + self.request.get("comment")
        sender_address = get_user_email() #not sure if we want to do this
        question = self.request.get("id")
        body = body + "\nVisit the question here: aecs1980qg.appspot.com/ReviewQuestion?id=" + question  
        subject = "Question " + question + " has been reported"
        mail.send_mail(sender_address , "bogdanbg24@gmail.com" , subject, body)
        self.redirect("/ReviewNewQuestions")

class addVote(webapp2.RequestHandler):
    def post(self):
        id = self.request.get("id")
        email = get_user_email()
        models.addVote(id,email)
        time.sleep(1)
        self.redirect("/ReviewNewQuestions") #maybe want a confirmation page
        
class decVote(webapp2.RequestHandler):
    def post(self):
        id = self.request.get("id")
        email = get_user_email()
        models.decVote(id,email)
        time.sleep(1)
        self.redirect("/ReviewNewQuestions")
        
###############################################################################
mappings = [
  ('/', MainPageHandler),
  ('/profile', ProfileHandler),
  ('/submitNew', SubmitPageHandler),
  ('/NewQuestion', NewQuestion),
  ('/ReviewQuestion', ReviewSingleQuestion),
  ('/meanstackakalamestack', test),
  ('/ReviewNewQuestions', ReviewNewQuestions),
  ('/ReviewOldQuestions', ReviewOldQuestions),
  ('/AnswerQuestion', AnswerQuestion),
  ('/submitQuiz',submitQuiz),
  ('/answerSingle',answerSingle),
  ('/submitAnswer',submitAnswer),
  ('/report', reportHandler),
  ('/incrementVote' , addVote),
  ('/decrementVote', decVote),
]
app = webapp2.WSGIApplication(mappings, debug=True)
