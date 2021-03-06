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
import time


JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)+"/"))

#User Model class
class Users(ndb.Model):
  Users_Emailaddress = ndb.StringProperty()
  Users_Name=ndb.StringProperty()
  Users_Followers=ndb.StringProperty(repeated=True)
  Users_Following=ndb.StringProperty(repeated=True)



class Comments(ndb.Model):
    Comment_uid=ndb.StringProperty()
    Comment_content=ndb.StringProperty()
    Comment_owner=ndb.StringProperty()
    comment_postuid=ndb.StringProperty()
    comment_time=ndb.StringProperty()

#Posts Model Class
class Post(ndb.Model):
  Post_Uid=ndb.StringProperty()
  Post_Caption=ndb.StringProperty()
  Post_Imgfilename=ndb.StringProperty()
  Post_Blob=ndb.StringProperty()
  Post_timestamp=ndb.StringProperty()
  Post_owner=ndb.StringProperty()
  Post_comments = ndb.StructuredProperty(Comments, repeated=True)
#Landing page does the authentication
class LoginPage(webapp2.RequestHandler):
    def get(self):
        url = ''
        url_string = ''
        welcome = 'Welcome back'
        myuser = None
        result= None
        finalposts=[]
        commentslist=[]
        usersinsystem=[]



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
                #posts=Post.query()
                #postsbyowner=posts.order(-Post.Post_timestamp).filter(Post.Post_owner==users.get_current_user().email()).fetch()
                #finalposts=postsbyowner
                followinglist=userdata.Users_Following
                print('followingslist')
                followinglist.remove('')
                print(followinglist)
                keys=[]

                for i in followinglist:
                    postsquery=Post.query().filter(Post.Post_owner==i).fetch(keys_only=True)
                    for il in postsquery:
                        keys.append(il)
            #     print('postquery')
        #         print(postsquery.fetch())
                postsquery=Post.query().filter(Post.Post_owner==user.email())

                tempo = postsquery.fetch(keys_only=True)
                print('tempo')
                print(tempo)
                if len(tempo)>0:
                    for ill in tempo:
                        keys.append(ill)

                temp=list(postsquery.fetch(keys_only=True))
                print(temp)
                print('keys')
                print(keys)
                finalposts=ndb.get_multi(keys)
                if postsquery!=None  :
                #    key=lambda x: x.name
                    finalposts.sort(key=lambda x: x.Post_timestamp, reverse=True)

                # followinglist=userdata.Users_Following
                # if len(finalposts)!=50:
                #     for i in followinglist:
                #         temposts=posts.order(-Post.Post_timestamp).filter(Post.Post_owner==i).fetch()
                #         for k in temposts:
                #             finalposts.append(k)

                    finalposts=finalposts[0:50]
                for i in finalposts:
                    cm=Comments.query().filter(Comments.comment_postuid==i.Post_Uid).fetch()
                    if len(commentslist)<1:
                        commentslist=cm
                    else:
                        commentslist.append(cm)



            result=[]
            #query only to get users
            print('comment')
            print(commentslist)
            q=Users.query()
            us =q.fetch()
            for i in us:
              usersinsystem.append(i.Users_Emailaddress)
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
            'finalposts':finalposts,
            'comments':commentslist,
            'usersinsystem':usersinsystem
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
            'finalposts':finalposts,
            'comments':commentslist,
            'usersinsystem':usersinsystem

             #           'img':img


        }
        print('usersinsystem')
        print(usersinsystem)
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
                #print(posts)
                print('profile data')
                print(profiledata.Users_Following)

                template = JINJA_ENVIRONMENT.get_template('Profile.html')
                template_values = {
                    'followers' : followersct,
                    'following' : followingct,
                    'posts':posts,
                    'role':role,
                    'email':email,
                    'profiledata':profiledata.Users_Following,
                    'users':users.get_current_user().email(),
                    'url':users.create_logout_url('/')


                }
                self.response.write(template.render(template_values))
            else:
                self.response.headers['Content-Type'] = 'text/html'
                self.response.write('Oops..!!! Seems like there are no users with this email id.')



class SearchProfile(webapp2.RequestHandler):
    def get(self):
        if self.request.get('SearchView'):
            userslist=Users.query()
            userslist=userslist.filter(Users.Users_Emailaddress==self.request.get('email')).fetch()



            template = JINJA_ENVIRONMENT.get_template('Profileslist.html')
            template_values = {
                'result':userslist,
                'email':self.request.get('email'),
                'users':users.get_current_user().email(),
                'url':users.create_logout_url('/')


            }
            self.response.write(template.render(template_values))

class FollowingFollowerslist(webapp2.RequestHandler):
    def get(self):
        if self.request.get('Followers'):
            usersinsystem=[]
            q=Users.query()
            us =q.fetch()
            for i in us:
              usersinsystem.append(i.Users_Emailaddress)
            if(users.get_current_user().email() in usersinsystem):
              usersinsystem.remove(users.get_current_user().email())
            email=urlparse(self.request.get('email'))
            followers=ndb.Key(Users,email.path).get()
            result=[]
            if(followers!=None and followers.Users_Followers!=None):
                result=followers.Users_Followers
            print('followers')
            print(result)
            template = JINJA_ENVIRONMENT.get_template('followersfollowings.html')
            template_values = {
                'result':result,
                'email':self.request.get('email'),
                'type':'followers',
                'usersinsystem':usersinsystem,
                'users':users.get_current_user().email(),
                'url':users.create_logout_url('/')



            }
            self.response.write(template.render(template_values))
        if self.request.get('Followings'):
            email=urlparse(self.request.get('email'))
            followings=ndb.Key(Users,email.path).get()
            result=[]
            if(followings!=None and followings.Users_Followers!=None):
                result=followings.Users_Following
            print('followings')
            print(result)
            template = JINJA_ENVIRONMENT.get_template('followersfollowings.html')
            template_values = {
                'result':result,
                'email':self.request.get('email'),
                'type':'followings',
                'users':users.get_current_user().email(),
                'url':users.create_logout_url('/')




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

class UnFollowUser(webapp2.RequestHandler):
    def get(self):
    #    followeremail=urlparse(self.request.get('followeremail'))
        followingemail=urlparse(self.request.get('followingemail'))
        followeruser=ndb.Key(Users,users.get_current_user().email()).get()
        followerslist1=followeruser.Users_Following
        followerslist1.remove(followingemail.path)
        followeruser.put()
        followinguser=ndb.Key(Users,followingemail.path).get()
        followinglist2=followinguser.Users_Followers
        followinglist2.remove(users.get_current_user().email())
        followinguser.put()
        self.redirect('/')        

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
    	print('Ghena')
    	upload = self.get_uploads()[0]
        now = datetime.now()
		# dd/mm/YY H:M:S
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        uidala=str(uuid.uuid4().hex)
        newpost= Post(id=uidala )
        newpost.Post_Caption=self.request.get('caption')
        newpost.Post_Imgfilename='blah'
        newpost.Post_Blob=get_serving_url(upload.key())
        newpost.Post_Uid=uidala
        new_address = Comments(Comment_content='None',Comment_owner='None',comment_postuid='None')
        newpost.Post_comments.append(new_address)


        newpost.Post_timestamp=dt_string
        newpost.Post_owner=users.get_current_user().email()

        newpost.put()
        time.sleep(1)
        self.redirect('/')

class Comment(webapp2.RequestHandler):
    def get(self):
        if self.request.get('CommentView'):
            usersinsystem=[]
            q=Users.query()
            us =q.fetch()
            for i in us:
              usersinsystem.append(i.Users_Emailaddress)
            if(users.get_current_user().email() in usersinsystem):
              usersinsystem.remove(users.get_current_user().email())
            template = JINJA_ENVIRONMENT.get_template('Addcomment.html')
            template_values = {
                'postid':self.request.get('postid'),
                'email':self.request.get('email'),
                'usersinsystem':usersinsystem,
                'user':users.get_current_user().email(),
                'url':users.create_logout_url('/')


            }
            self.response.write(template.render(template_values))
        if self.request.get('Submit'):
            uidl=str(uuid.uuid4().hex)
            kk=ndb.Key(Post,self.request.get('postid')).get()
            print('aliya')
            print(kk)
            new_address = Comments(id=uidl,comment_time=str(datetime.today().strftime('%Y-%m-%d %H:%M:%S')),Comment_content=self.request.get('comment'),Comment_owner=users.get_current_user().email(),comment_postuid=self.request.get('postid'))
            kk.Post_comments.append(new_address)

            kk.put()

            time.sleep(1)
            self.redirect('/')

class ViewComments(webapp2.RequestHandler):
    def get(self):
        postuid=self.request.get('postuid')
        template = JINJA_ENVIRONMENT.get_template('commentsview.html')
        usersinsystem=[]
        q=Users.query()
        us =q.fetch()
        for i in us:
          usersinsystem.append(i.Users_Emailaddress)
        if(users.get_current_user().email() in usersinsystem):
          usersinsystem.remove(users.get_current_user().email())    
        post=ndb.Key(Post,postuid).get()
        comments=post.Post_comments
        template_values = {
            'comments':comments,
            'users':users.get_current_user().email(),
            'url':users.create_logout_url('/'),
            'usersinsystem':usersinsystem



        }
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/', LoginPage),('/ViewComments',ViewComments),('/Comment',Comment),('/UploadHandler',UploadHandler),('/FollowingFollowerslist',FollowingFollowerslist),('/FollowUser',FollowUser),('/UnFollowUser',UnFollowUser),('/Profile',Profile),('/SearchProfile',SearchProfile)
], debug=True)
