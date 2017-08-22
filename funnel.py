import os
from contextlib import contextmanager
import jinja2
from PIL import Image
from StringIO import StringIO
import requests
import shutil
import multiprocessing
import json

class Funnel(object):
  """
    Funnel is a flask website generator and provides a way to quickly
    build websites and push them to heroku. It removes boilerplate setup
    for simple apps.
  """
  def __init__(self, app_name="", logo_url="", pages="", email="", google_analytics="", **kwargs):
    self.environment = jinja2.Environment(loader=jinja2.FileSystemLoader('templates/'))
    self.app_name = app_name.lower().replace(" ", "_")
    self.logo_url = logo_url
    self.pages = [page.lower().replace(" ", "_") for page in pages if len(page) > 0]
    self.email = email
    self.google_analytics = google_analytics
    if len(logo_url) > 0:
      response = requests.get(logo_url)
      self.logo_file = Image.open(StringIO(response.content))
      self.logo_file = self.logo_file.convert('RGB')
      self.colors = self.logo_file.getcolors()
      self.colors = sorted(self.colors)[-1:-6:-1]
      self.colors = ["#{:02x}{:02x}{:02x}".format(color[1][0],color[1][1],color[1][2]) for color in self.colors]

  @contextmanager
  def cwd(self, path):
    """
    Simple context manager to change directories and change back after
    finishing with command.

    Used as with cwd('/some/directory'):
    """
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
      yield
    finally:
      os.chdir(oldpwd)

  def app_command(self, command, silence_output=False):
    """
    Function to execute a system command in the root directory of an application.
    Enters the app's directory, executes a command, and returns to the previous working
    directory.
    :param command: (str) Command to be executed.
    :return:
    """
    with self.cwd("applications/{}".format(self.app_name)):
      try:
        if silence_output:
          os.system(command + " >/dev/null 2>&1")
        else:
          os.system(command)
      except Exception as e:
        print e
        print "Could not execute command '" + command + "'"

  def generate_app(self):
    """
    Function to generate an app. Creates all necessary files and directories.
    :return:
    """
    # Create app directories
    directories = [
      "applications/{}".format(self.app_name),
      "applications/{}/static".format(self.app_name),
      "applications/{}/templates".format(self.app_name),
      "applications/{}/static/js".format(self.app_name),
      "applications/{}/static/img".format(self.app_name),
      "applications/{}/static/css".format(self.app_name),
      "applications/{}/static/css/fonts".format(self.app_name)
    ]
    for directory in directories:
      if not os.path.exists(directory):
        os.makedirs(directory)
      else:
        print "Directory {} already exists".format(directory)
    # Save a copy of the logo file
    if self.logo_file:
      self.logo_file.save("applications/{}/static/img/logo.png".format(self.app_name))
    # Get app template
    template = self.environment.get_template('flask/app.template')
    # Create app.py
    with open("applications/{}/app.py".format(self.app_name), "w") as f:
      f.write(template.render(pages=[page.replace(" ","_") for page in self.pages]))
    # Copy necessary files into new application
    shutil.copy2("templates/css/base.css", "applications/{}/static/css/base.css".format(self.app_name))
    shutil.copy2("templates/css/base.css", "applications/{}/static/css/theme.css".format(self.app_name))
    # Create base html
    with open("applications/{}/templates/base.html".format(self.app_name), "w") as f:
      template = self.environment.get_template("html/base.html")
      f.write(template.render(logo=self.logo_url, pages=self.pages))
    # Create base js
    with open("applications/{}/static/js/base.js".format(self.app_name), "w") as f:
      template = self.environment.get_template("js/base.js")
      f.write(template.render(google_analytics=self.google_analytics))
    # Create empty theme js
    open("applications/{}/static/js/theme.js".format(self.app_name), 'a').close()
    # Create page templates
    self.create_page("home")
    for page in self.pages:
      self.create_page(page)
    self.create_page("contact")
    # Export app.
    self.export_app()
    # Setup git
    self.setup_git()

  def export_app(self, save_to_file=True):
    """
    Function to export instance variables of an app.

    :param save_to_file: (bool) Whether or not to write to funnel.json, default = True
    :return:
    """
    #Create the funnel json for export
    unwanted_variables = ["environment", "logo_file"]
    funnel_dict = {el:self.__dict__[el] for el in [key for key in self.__dict__ if key not in unwanted_variables]}
    if save_to_file:
      with open("applications/{}/funnel.json".format(self.app_name), "w") as f:
        f.write(json.dumps(funnel_dict))
    return funnel_dict

  def change_css(self, theme_file):
    """

    :param theme_file: (str) name of css theme. For example "paper.css"
    :return:
    """
    shutil.copy2(
      "templates/css/{}".format(theme_file),
      "applications/{}/static/css/theme.css".format(self.app_name))

  def create_page(self, page):
    """
    Function To create the "middle" pages of the app.
    Home page and contact page are inferred. Built off
    the base and a page.html template.

    :param page: (str) Name of page to be created.
    :return:
    """
    shutil.copy2(
      "templates/html/page.html",
      "applications/{}/templates/{}.html".format(self.app_name, page))

  def start_app(self):
    """
    Starts the flask app locally on port 5000. Starts in flask in debug mode.
    :return:
    """
    try:
      background_server = multiprocessing.Process(target=self.app_command, args=("FLASK_APP=app.py FLASK_DEBUG=1 python -m flask run",))
      background_server.start()
      print "* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)"
    except Exception as e:
      print e
      print "Could not start server."
    return background_server

  def setup_git(self):
    """
    Function to initialize git repo and create master and staging branches.
    :return:
    """
    # Initialize git repo in application directory.
    self.app_command("git init")
    # Add files
    self.app_command("git add -A")
    # Stage first commit
    self.app_command("git commit -m \"First commit\"")
    # Create staging branch locally.
    self.app_command("git checkout -b staging")
    # Create master branch locally.
    self.app_command("git checkout master")

  def setup_heroku(self):
    """
    Using this function requires the heroku cli to be installed.


    It sets up a staging and production application.
    :return:
    """
    # Copy files necessary for heroku into application directory.
    shutil.copy2("templates/flask/heroku/Procfile", "applications/{}/".format(self.app_name))
    shutil.copy2("templates/flask/heroku/requirements.txt", "applications/{}/requirements.txt".format(self.app_name))
    try:
      self.app_command("heroku create {}-production".format(
        self.app_name.replace("_", "-")))
      self.app_command("heroku create {}-staging --remote staging".format(
        self.app_name.replace("_", "-")))
    except Exception as e:
      print e
      print "Could not create a heroku app. Either an app exists with this name or heroku is not configured."
      return
    self.staging = "https://{}-staging.herokuapp.com/".format(self.app_name.replace("_", "-"))
    self.staging_repo = "https://git.heroku.com/{}.git".format(self.app_name.replace("_", "-")+"-staging")
    self.production = "https://{}-production.herokuapp.com/".format(self.app_name.replace("_", "-"))
    self.production_repo = "https://git.heroku.com/{}.git".format(self.app_name.replace("_", "-")+"-production")

  def setup_github(self):
    """
    Using this functions requires the hub cli git extension by github.
    Avalaible at https://github.com/github/hub/releases

    The function will create a private github repository for the new app.
    :return:
    """
    # Creates the repo for the app.
    self.app_command("hub create -p nametailorllc/{}".format(self.app_name))
    self.app_command("git push origin master")
    self.app_command("git push origin staging")


  def stage_app(self, commit_message=""):
    """
    Pushes code to heroku staging environment. Or creates one if necessary.
    Pushes code to staging branch of github repo.
    :return:
    """
    if len(commit_message) == 0:
      commit_message = "Staging commit: Uncommented."
    self.app_command("git add -A")
    self.app_command("git commit -m \"{}\"".format(commit_message))
    self.app_command("git push origin staging")
    self.app_command("git push staging master")

  def deploy_app(self, commit_message=""):
    """
    Pushes code to heroku production environment. Or creates one if necessary.
    Pushes code to master branch of github repo.
    Function to deploy the flask app to heroku.
    :return:
    """
    if len(commit_message) == 0:
      commit_message = "Deployment commit: Uncommented."
    self.app_command("git add -A")
    self.app_command("git commit -m \"{}\"".format(commit_message))
    self.app_command("git push origin master")
    self.app_command("git push heroku master")