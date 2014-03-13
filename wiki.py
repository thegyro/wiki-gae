import webapp2
import jinja2
import os
import validation
import utils
import time
from wiki_db import User,Page

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self,*a,**kw):
        self.response.out.write(*a,**kw)

    def render_str(self,template,**params):
        t = jinja_env.get_template(template)
        params['user'] = self.user
        return t.render(params)

    def render(self,template,**kw):
        self.write(self.render_str(template,**kw))

    def set_secure_cookie(self,name,val):
        cookie_val = utils.make_secure_val(val)
        self.response.headers.add_header('Set-Cookie','%s=%s; Path=/' %(name,cookie_val))

    def read_secure_cookie(self,name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and utils.check_secure_val(cookie_val)

    def login(self,user):
        self.set_secure_cookie('user_id',str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie','user_id=; Path=/')

    def initialize(self,*a,**kw):
        webapp2.RequestHandler.initialize(self,*a,**kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))
        
class WikiPage(Handler):
    def get(self,page_id):
        page_id = page_id[1:]
        if page_id:
            p = Page.by_page_id(page_id)
            if p:
                self.render('base.html',page=p,id=page_id)
            else:
                self.redirect('/_edit/%s' % page_id)

        else:
            p = Page.by_page_id('/')
            self.render('base.html',page=p)
            
class Signup(Handler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get("username")
        self.password = self.request.get("password")
        self.verify = self.request.get("verify")
        self.email = self.request.get("email")

        params,have_error = validation.validate(self.username,self.password,self.verify,self.email)

        if have_error:
            self.render("signup-form.html",**params)

        else:
            u = User.by_name(self.username)
            if u:
                msg = 'That user already exists.'
                self.render('signup-form.html',err_uname=msg)
            else:
                u = User.register(self.username,self.password,self.email)
                u.put()
                self.login(u)
                self.redirect('/')

class Login(Handler):
    def get(self):
        cookie = self.request.cookies.get('user_id')
        if cookie and utils.check_secure_val(cookie):
            self.redirect('/')
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username,password)

        if u:
            self.login(u)
            self.redirect('/')
        else:
            msg = 'Invalid Login'
            self.render('login-form.html',error = msg)

class Logout(Handler):
    def get(self):
        self.logout()
        self.redirect('/')


class EditPage(Handler):
    def get(self,page_id):
        page_id = page_id[1:]
        if self.user:
            if page_id:
                p = Page.by_page_id(page_id)
                if p:
                    self.render('page.html',page=p)
                else:
                    self.render('page.html',page=None)
            else:
                p = Page.by_page_id('/')
                self.render('page.html',page=p)
        else:
            self.redirect('/login')

    def post(self,page_id):
        page_id = page_id[1:]
        page_html = self.request.get('content')
        
        if page_id:
            p = Page.by_page_id(page_id)
            if p:
                p.html = page_html
                p.put()
                time.sleep(1)
                self.redirect('/%s' % page_id)

            else:
                p = Page(html=page_html,page_id=page_id)
                p.put()
                time.sleep(1)
                self.redirect('/%s' % page_id)
        else:
            p = Page.by_page_id('/')
            if p:
                p.html = page_html
            else:
                p = Page(html=page_html,page_id='/')

            p.put()
            time.sleep(1)
            self.redirect('/')

PAGE_RE = r"(/(?:[a-zA-Z0-9_-]+/?)*)"
app = webapp2.WSGIApplication([('/signup',Signup),
                               ('/login',Login),
                               ('/logout',Logout),
                               ('/_edit' + PAGE_RE,EditPage),
                               (PAGE_RE,WikiPage)],
                               debug= True)
