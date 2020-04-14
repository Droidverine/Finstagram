import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from datetime import datetime
import uuid

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)+"/"))

#User Model class
class Users(ndb.Model):
  Users_Emailaddress = ndb.StringProperty()
  Users_Followers=ndb.StringProperty(repeated=True)
  Users_Following=ndb.StringProperty(repeated=True)
  Users_Posts = ndb.BlobKeyProperty(repeated=True)

#Posts Model Class
class Post(ndb.Model):
  Post_Uid=ndb.StringProperty()
  Post_Caption=ndb.StringProperty()
  Post_Imgfilename=ndb.StringProperty()
  Post_Blob=ndb.BlobKeyProperty()
  Post_timestamp=ndb.StringProperty()
  Post_owner=ndb.StringProperty()


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
        upload_url = blobstore.create_upload_url('/UploadHandler')



        if( myuser == None):

          template_values = {
            'url' : url,
            'url_string' : url_string,
            'user' : user,
            'welcome' : welcome,
            'myuser' : myuser,
            'upload_url':upload_url


        }
        else:
          template_values = {
            'url' : url,
            'url_string' : url_string,
            'user' : user,
            'welcome' : welcome,
            'myuser' : myuser,
            'upload_url':upload_url

        }
        self.response.write(template.render(template_values))



class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
    	print('Ghena')

    	upload = self.get_uploads()[0]
    	userposts=ndb.Key(Users,users.get_current_user().email()).get()
    	result=[]
    	if userposts.Users_Posts !=None:
    		result=userposts.Users_Posts
    		result.append(upload.key())
    		userposts.Users_Posts=result
    		userposts.put()
    	else:	
    		result.append(upload.key())
    		userposts.Users_Posts=result
    		userposts.put()
        
        now = datetime.now()
 

		# dd/mm/YY H:M:S
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        newpost= Post(id= str(uuid.uuid4().hex))
        newpost.Post_Caption=self.request.get('caption')
        newpost.Post_Imgfilename='blah'
        newpost.Post_Blob=upload.key()
        newpost.Post_timestamp=dt_string
        newpost.Post_owner=users.get_current_user().email()

        newpost.put()
        self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', LoginPage),('/UploadHandler',UploadHandler)
], debug=True)
