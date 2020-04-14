import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import blobstore


JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)+"/"))

#User Model class
class Users(ndb.Model):
  Users_Emailaddress = ndb.StringProperty()
  Users_Followers=ndb.StringProperty(repeated=True)
  Users_Following=ndb.StringProperty(repeated=True)

#Posts Model Class
class Post(ndb.Model):
  Post_Uid=ndb.StringProperty()
  Post_Caption=ndb.StringProperty()
  Post_Imgfilename=ndb.StringProperty()
  Post_Blob = ndb.BlobKeyProperty(repeated=True)


#Landing page does the authentication
class LoginPage(webapp2.RequestHandler):
    def get(self):
        url = ''
        url_string = ''
        welcome = 'Welcome back'
        myuser = None
        result= None

        user = users.get_current_user()

        if user:
            #if user succesfully logged in
            url = users.create_logout_url('/')
            url_string = 'logout'
            myuser_key = ndb.Key('Users', user.email())
            myuser = myuser_key.get()
            template = JINJA_ENVIRONMENT.get_template('Home.html')
            userdata = ndb.Key('Users', user.email()).get()
            result=[]
            #query only to get users

            q=Users.query()
            us =q.fetch()
            usersinsystem=[]
            for i in us:
              usersinsystem.append(i.Users_Emailaddress)
            usersinsystem.append('')
            if(user.email() in usersinsystem):
              usersinsystem.remove(user.email())






            if myuser == None:
                #if user info not in database insert.
                welcome = 'Welcome to the application'
                abc=['ep']
                myuser = Users(id=user.email())
                myuser.Users_Emailaddress = user.email()
                myuser.Users_Following=['']
                myuser.Users_Followers=['']
                myuser.put()


        else:
            #if user not logged in.
            url = users.create_login_url(self.request.uri)
            url_string = 'login'
            template = JINJA_ENVIRONMENT.get_template('Login.html')



        if( myuser == None):
          template_values = {
            'url' : url,
            'url_string' : url_string,
            'user' : user,
            'welcome' : welcome,
            'myuser' : myuser,


        }
        else:
          template_values = {
            'url' : url,
            'url_string' : url_string,
            'user' : user,
            'welcome' : welcome,
            'myuser' : myuser,

        }
        self.response.write(template.render(template_values))




app = webapp2.WSGIApplication([
    ('/', LoginPage)
], debug=True)
