import os
import jinja2
from PIL import Image
from StringIO import StringIO
import requests


class Funnel(object):
  def __init__(self, company_name, logo_url, pages, email, google_analytics):
    self.environment = jinja2.Environment(loader=jinja2.FileSystemLoader('templates/flask'))
    self.app_name = company_name.lower().replace(" ", "_")
    self.logo_url = logo_url
    self.pages = [page.lower() for page in pages]
    self.email = email
    self.google_analytics = google_analytics
    response = requests.get(logo_url)
    img = Image.open(StringIO(response.content)).convert('RGB')
    self.logo_colors = img.getcolors()

  def generate_app(self):
    # Create app directories
    os.system("mkdir applications/{}".format(self.app_name))
    # Get app template
    template = self.environment.get_template('app.py')
    # Create app.py
    with open("applications/{}/app.py".format(self.app_name), "w") as f:
      f.write(template.render(pages=self.pages))
    # Create template directory.
    os.system("mkdir -p applications/{}/templates".format(self.app_name))
    # Create static directory and copy base javascript.
    os.system(("mkdir -p applications/{}/static").format(self.app_name))
    os.system(("mkdir -p applications/{}/static/js").format(self.app_name))
    os.system(("mkdir -p applications/{}/static/img").format(self.app_name))
    os.system(("mkdir -p applications/{}/static/css").format(self.app_name))
    os.system(("cp templates/flask/templates/theme.css applications/{}/static/css/theme.css").format(self.app_name))
    os.system("cp templates/flask/templates/theme.js applications/{}/static/js/theme.js".format(self.app_name))
    # Create base template
    with open("applications/{}/templates/base.html".format(self.app_name), "w") as f:
      template = self.environment.get_template("templates/base.html")
      f.write(template.render(logo=self.logo_url, pages=self.pages))
    # Create page templates
    self.create_page(self.app_name, "home")
    for page in self.pages:
      self.create_page(self.app_name, page)
    self.create_page(self.app_name, "contact")

  def change_theme(self, theme_file):
    os.system(
      "cp templates/flask/themes/{} applications/{}/static/css/theme.css".format(theme_file, self.app_name))

  def create_page(self, app_name, page):
    os.system("cp templates/flask/templates/page.html applications/{}/templates/{}.html".format(app_name, page))

  def start_app(self):
    os.system("python applications/{}/app.py".format(self.app_name))
