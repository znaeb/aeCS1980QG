import cgi
import webapp2
import models
import datetime
import logging
import os
import time
#import json

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import ndb
#from google.appengine.api import images
#from google.appengine.ext import blobstore
#from google.appengine.ext.webapp import blobstore_handlers


MAIN_PAGE_HTML = """\
<html>
  <head>
    <meta charset="UTF-8">
    <title>Add a Question</title>
        <link rel="stylesheet" href="stylesheets/style.css">
  </head>
  <body>
<form action=/NewQuestion method="post"><font size = 4>
  Category:
  <input list="Category" name="category" method=POSTrequired>
  <datalist id="Category">
    <option value="PHARM 2001">
    <option value="PHARM 3023">
    <option value="PHARM 3028">
    <option value="PHARM 3040">
    <option value="PHARM 5218">
  </datalist>
</br>
  Question:
  <input type="text" size = "45" name="questiontext"method=POST required>
  <hr>
  <ol>
    <li class="red-text">
      <input type="text" method=POST name="answer1" required>
    </li>
    <li class="blue-text">
      <input type="text" method=POST name="answer2" required>
    </li>
    <li class="green-text">
      <input type="text" method=POST name="answer3" required>
    </li>
    <li class="yellow-text">
      <input type="text" method=POST name="answer4" required>
    </li>
  </ol>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <button type="submit" name="answerid" value=1 class="red-text">1</button>
    <button type="submit" name="answerid" value=2 class="blue-text">2</button>
    <button type="submit" name="answerid" value=3 class="green-text">3</button>
    <button type="submit" name="answerid" value=4 class="yellow-text">4</button>
  </form>
</font>
</body>
</html>
"""

REVIEW_PAGE_HTML = """\
<html>
<link rel="stylesheet" href="stylesheets/style.css">
<body>
  <div class = "container">
    <br><br><br>
    <p>Here is a new user question:</p>
    <p>Who is the spiciest chili pepper at Pitt?</p>
    <ol>
      <li class="red-text">Bill Laboon</li>
      <li class="blue-text">Nick Farnan</li>
      <li class="green-text">Jon Misurda</li>
      <li class="yellow-text">Taieb Znati</li>
    </ol>
    <p>The answer is:</p><p class = "red-text">Bill Laboon</p>
    <p>Should this question be added?</p>
    <form action="submit-review">
      <button type="submit" name=yes>Yes</button>
      <button type="submit" name=no>No</button>
    </form>
"""

def render_template(handler, templatename, templatevalues={}):
  path = os.path.join(os.path.dirname(__file__), 'templates/' + templatename)
  html = template.render(path, templatevalues)
  handler.response.out.write(html)

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write(MAIN_PAGE_HTML)

class NewQuestion(webapp2.RequestHandler):
    def post(self):
        category = self.request.get('category')
        question = self.request.get('questiontext')
        answer1 = self.request.get('answer1')
        answer2 = self.request.get('answer2')
        answer3 = self.request.get('answer3')
        answer4 = self.request.get('answer4')
        answerid = self.request.get('answerid')
        questionID = models.create_question(category,question,answer1,answer2,answer3,answer4,answerid)
        self.response.write('<html><body>You wrote:<pre>')
        self.response.write(category)
        self.response.write(questionID)
        self.response.write('</br>'+question)
        self.response.write('</br>'+answer1)
        self.response.write('</br>'+answer2)
        self.response.write('</br>'+answer3)
        self.response.write('</br>'+answer4)
        self.response.write('</br>The answer is: '+answerid)
        self.response.write('</pre>')
        self.response.write('<p>Would you like to review the question now?</p>')
        self.response.write('<form action="ReviewQuestion"><button type="submit" name=yes value=')
        self.response.write(questionID)
        self.response.write('>')
        self.response.write('Yes</button><button type="submit" name=no>No</button>')
        self.response.write('</form>')
        self.response.write('</body></html>')

class ReviewQuestion(webapp2.RequestHandler):
    def get(self):
        #just loops and prints every question from query
        review = models.get_oldest_questions()
        # for question_obj in review:
            # self.response.write('<html><link rel="stylesheet" href="stylesheets/style.css">')
            # self.response.write('<body><div class = "container"><br>')
            # self.response.write('<p>Here is a new user question: ')
            # self.response.write('<p>')
            # self.response.write(question_obj.question)  #question
            # self.response.write('</p><ol>')
            # self.response.write('<li class="red-text">')
            # self.response.write(question_obj.answer1)                                #answer1
            # self.response.write('</li>')
            # self.response.write('<li class="blue-text">')
            # self.response.write(question_obj.answer2)                                #answer2
            # self.response.write('</li>')
            # self.response.write('<li class="green-text">')
            # self.response.write(question_obj.answer3)                                #answer3
            # self.response.write('</li>')
            # self.response.write('<li class="yellow-text">')
            # self.response.write(question_obj.answer4)                                #answer4
            # self.response.write('</li></ol>')
            # self.response.write('<p>The answer is:</p><p class = "red-text">')
            # self.response.write(question_obj.answerid)                                #answerid
            # self.response.write('</p>')
            # self.response.write('<p>Should this question be added?</p>')
            # self.response.write('<form action="submit-review">')
            # self.response.write('<button type="submit" name=yes>Yes</button>')
            # self.response.write('<button type="submit" name=no>No</button>')
            # self.response.write('</form>')
            # self.response.write("</div></body></html>")
        page_params = {
          'login_url': users.create_login_url(),
          'logout_url': users.create_logout_url('/'),
          'review': review,
        }
        render_template(self, 'newQuestionReview.html', page_params)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/NewQuestion', NewQuestion),
    ('/ReviewQuestion',ReviewQuestion)
], debug=True)