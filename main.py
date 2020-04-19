import webapp2
import jinja2
import os
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from datetime import datetime
import uuid
from urlparse import urlparse, parse_qs
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api.images import get_serving_url


JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)+"/"))

#User Model class
class Users(ndb.Model):
  Users_Emailaddress = ndb.StringProperty()
  Users_Name=ndb.StringProperty()
  Users_Followers=ndb.StringProperty(repeated=True)
  Users_Following=ndb.StringProperty(repeated=True)

#Posts Model Class
class Post(ndb.Model):
  Post_Uid=ndb.StringProperty()
  Post_Caption=ndb.StringProperty()
  Post_Imgfilename=ndb.StringProperty()
  Post_Blob=ndb.StringProperty()
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
        finalposts=[]

        user = users.get_current_user()

        if user:
            #if user succesfully logged in
            url = users.create_logout_url('/')
            url_string = 'logout'
            myuser_key = ndb.Key('Users', user.email())
            myuser = myuser_key.get()
            template = JINJA_ENVIRONMENT.get_template('Home.html')
            userdata = ndb.Key('Users', user.email()).get()
            if userdata!=None:
                posts=Post.query()
                postsbyowner=posts.order(-Post.Post_timestamp).filter(Post.Post_owner==users.get_current_user().email()).fetch()
                finalposts=postsbyowner
                followinglist=userdata.Users_Following
                if len(finalposts)!=50:
                    for i in followinglist:
                        temposts=posts.order(-Post.Post_timestamp).filter(Post.Post_owner==i).fetch()
                        for k in temposts:
                            finalposts.append(k)

                finalposts=finalposts[0:50]

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
      #  img=get_serving_url('hPZlWG4cAK5HbH2NUJ1p8w==')
      #  print('serving url')
       # print(img)




        if( myuser == None):

          template_values = {
            'url' : url,
            'url_string' : url_string,
            'user' : user,
            'welcome' : welcome,
            'myuser' : myuser,
            'upload_url':upload_url,
            'finalposts':finalposts
            #'img':img


        }
        else:
          template_values = {
            'url' : url,
            'url_string' : url_string,
            'user' : user.email(),
            'welcome' : welcome,
            'myuser' : myuser,
            'upload_url':upload_url,
            'finalposts':finalposts
             #           'img':img


        }
        print('finalsposts')
        print(finalposts)
        self.response.write(template.render(template_values))

class Profile(webapp2.RequestHandler):
    def get(self):
        if self.request.get('ViewProfile'):
            email=urlparse(self.request.get('email'))
            email=email.path
            profiledata=ndb.Key(Users,email).get()
            role=None
            if profiledata!=None:
                followersct=len(profiledata.Users_Followers)
                followingct=len(profiledata.Users_Following)
                posts=Post.query()
                posts=posts.order(-Post.Post_timestamp).filter(Post.Post_owner==email).fetch()

            if users.get_current_user().email()==email:
                role='owner'
            else:
                role='visitor'

            profiledata=ndb.Key(Users,users.get_current_user().email()).get()

            print('posts')
            print(posts)
            print('profile data')
            print(profiledata.Users_Following)

            template = JINJA_ENVIRONMENT.get_template('Profile.html')
            template_values = {
                'followers' : followersct,
                'following' : followingct,
                'posts':posts,
                'role':role,
                'email':email,
                'profiledata':profiledata.Users_Following


            }
            self.response.write(template.render(template_values))

class SearchProfile(webapp2.RequestHandler):
    def get(self):
        if self.request.get('SearchView'):
            userslist=Users.query()
            userslist=userslist.filter(Users.Users_Emailaddress==self.request.get('email')).fetch()



            template = JINJA_ENVIRONMENT.get_template('Profileslist.html')
            template_values = {
                'result':userslist,
                'email':self.request.get('email')


            }
            self.response.write(template.render(template_values))

class FollowUser(webapp2.RequestHandler):
    def get(self):
    #    followeremail=urlparse(self.request.get('followeremail'))
        followingemail=urlparse(self.request.get('followingemail'))
        followeruser=ndb.Key(Users,users.get_current_user().email()).get()
        followerslist1=followeruser.Users_Following
        followerslist1.append(followingemail.path)
        followeruser.put()
        followinguser=ndb.Key(Users,followingemail.path).get()
        followinglist2=followinguser.Users_Followers
        followinglist2.append(users.get_current_user().email())
        followinguser.put()
        self.redirect('/')

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
    	print('Ghena')

    	upload = self.get_uploads()[0]


        now = datetime.now()


		# dd/mm/YY H:M:S
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        newpost= Post(id= str(uuid.uuid4().hex))
        newpost.Post_Caption=self.request.get('caption')
        newpost.Post_Imgfilename='blah'
        newpost.Post_Blob=get_serving_url(upload.key())

        newpost.Post_timestamp=dt_string
        newpost.Post_owner=users.get_current_user().email()

        newpost.put()
        self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', LoginPage),('/UploadHandler',UploadHandler),('/FollowUser',FollowUser),('/Profile',Profile),('/SearchProfile',SearchProfile)
], debug=True)
