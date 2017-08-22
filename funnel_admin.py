import funnel
import json
import zipfile
import os
from distutils.dir_util import copy_tree

def create_app():
  """
  Function to create a new app.
  :return:
  """
  app_name = raw_input("Company Name:")
  if len(app_name) == 0:
    app_name = "Example Company"
  logo_url = raw_input("Logo url:")
  if len(logo_url) == 0:
    logo_url = "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"
    #Clearline http://i.imgur.com/wc0nX3r.png
  page_names = raw_input("Page names separate by comma:")
  pages = [page.strip() for page in page_names.split(",")]
  if len(pages) == 0:
    pages = ["a","b","c"]
  email = "junk@data.com"
  google_analytics = "JUNKDATA"
  app = funnel.Funnel(app_name, logo_url, pages, email, google_analytics)
  app.generate_app()
  #app.setup_heroku()
  #app.setup_github()
  #app.stage_app("First stage")
  #app.deploy_app("First deployment")
  return app

def load_app(funnel_json_path, generate=False):
  """

  :param generate: (bool) Whether to generate files for the app or not. Default is false.
  :return:
  """
  app = None
  with open(funnel_json_path) as f:
    funnel_data = json.loads(f.read())
    print funnel_data
    app = funnel.Funnel(**funnel_data)
  if generate:
    app.generate_app()
  return app

def load_theme(theme_name, funnel_app):
  """

  :param theme_name: (str) File path to zipped theme.
  :param funnel_app:
  :return:
  """
  theme_archive = zipfile.ZipFile('templates/themes/{}.zip'.format(theme_name))
  if funnel_app and len(funnel_app.app_name) > 0:
    theme_archive.extractall(path="applications/{}/static/themes/{}".format(funnel_app.app_name,theme_name))

if __name__ == "__main__":
  # TODO write a proper CLI for the admin functions. Create, Load, Edit etc
  app = load_app("funnel.json", generate=True)
  server = app.start_app()
  while True:
    try:
      theme = raw_input("Theme:").lower().strip()
      load_theme(theme, app)
    except KeyboardInterrupt:
      print "Shutting down"
      app.export_app()
      server.terminate()
      exit()