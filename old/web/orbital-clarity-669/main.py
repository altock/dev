import webapp2
import cgi
import re
import jinja2
import os
import hmac
from google.appengine.ext import db
SECRET = "imsosecret"
def hash_str(s):
	return hmac.new(SECRET,s).hexdigest()

def make_secure_val(s):
	return "%s|%s" % (s,hash_str(s))

def check_secure_val(h):
	val = h.split('|')[0]
	if h == make_secure_val(val):
		return val

template_dir = os.path.join(os.path.dirname(__file__),'templates') 
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True) 
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$") 
def valid_username(username):
     return USER_RE.match(username) 

PASS_RE = re.compile(r"^.{3,20}$") 
def valid_password(password):
     return PASS_RE.match(password) 
def verify(password,verify):
     return password == verify

EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
def valid_email(email):
	return EMAIL_RE.match(email) or not email

form="""

"""
# That's not a valid username. That wasn't a valid password. Your passwords didn't match. That's not a valid email
class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a,**kw)

	def render_str(self,template, **params):
		t = jinja_env.get_template(template)
		return t.render(**params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class FizzBuzzHandler(Handler):
	def get(self):
		n = self.request.get('n', 0)
		n= n and int(n)
		self.render("fizzbuzz.html", n = n)
class Art(db.Model):
	title = db.StringProperty(required = True)
	art = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class AsciiHandler(Handler):
	def render_ascii(self, title="", art="",error=""):
		arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC")
		self.render("ascii.html", title=title, art=art, error=error, arts = arts)

	def get(self):
		self.render_ascii()

	def post(self):
		title = self.request.get("title")
		art = self.request.get("art")

		if title and art:
			a = Art(title = title, art = art)
			a.put()

			self.redirect("/ascii")
		else:
			error = "we need both a title and some artwork"
			self.render_ascii(title,art, error=error)

class Blog(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
class BlogHandler(Handler):
	def render_blog(self,error=""):
		blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")
		self.render("blog.html", error=error, blogs = blogs)

	def get(self):
		self.render_blog()

class FormHandler(Handler):
	def render_form(self, subject="", content="",error=""):
		self.render("form.html", subject=subject, content=content, error=error)

	def get(self):
		self.render_form()

	def post(self):
		subject = self.request.get("subject")
		content = self.request.get("content")

		if subject and content:
			a = Blog(subject = subject, content = content)
			a.put()
			self.redirect("/blog/%d" % (a.key().id()))
		else:
			error = "we need both a subject and some content"
			self.render_form(subject,content, error=error)

class ProductHandler(Handler):
	def get(self, iD):
		blog = Blog.get_by_id(int(iD))
		self.render("perma.html", blog = blog)


class SignUpPage(Handler):
	def write_form(self, username="", password="", verify="", email="", a = '', b = '', c = '', d = ''):
		self.render("signup.html", username = username, password = password, verify=  verify, email= email, a = a, b = b, c = c, d = d)
		

	def get(self):
		self.write_form()
		"""self.response.headers['Content-Type'] = 'text/plain'
		visits = 0
		visits_cookie_str = self.request.cookies.get('visits')
		if visits_cookie_str:
			cookie_val = check_secure_val(visits_cookie_str)
			if cookie_val:
				visits = int(cookie_val)
		
		visits += 1

		new_cookie_val = make_secure_val(str(visits))
		self.response.headers.add_header('Set-Cookie', 'visits=%s' % new_cookie_val)

		if visits > 10:
			self.write("You are the best ever!")
		else:
			self.write("You've been here %s times!" % visits)"""
		
		#self.write_form()
		#self.render('fizzbuzz.html')
	def post(self):
		
		user_name = valid_username(self.request.get('username'))
		user_pass = valid_password(self.request.get('password'))
		user_ver = verify(self.request.get('password'),self.request.get('verify'))
		user_email = valid_email(self.request.get('email'))
		if not (user_name and user_pass and user_ver and user_email):
			a = ""
			b = ""
			c = ""
			d = ""
			if not user_name:
				a = "That's not a valid username"
			if not user_pass:
				b = "That wasn't a valid password"
			if not user_ver:
				c = "Your passwords didn't match"
			if not user_email:
				d = "That's not a valid email"
			self.write_form(self.request.get('username'),"","",self.request.get('email'),a,b,c,d)
			
		else:
			self.redirect("/welcome?username="+self.request.get('username'))
		
class SucessPage(webapp2.RequestHandler):
	def get(self):
		q = self.request.get("username")
		self.response.out.write("Welcome, " + q+"!")
		#self.render('fizzbuzz.html')

app = webapp2.WSGIApplication([('/signup',SignUpPage),('/welcome',SucessPage),('/fizzbuzz',FizzBuzzHandler),('/ascii',AsciiHandler),('/blog',BlogHandler),('/blog/(\d+)',ProductHandler),('/blog/newpost',FormHandler)], debug=True)
