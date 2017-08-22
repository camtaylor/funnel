import funnel
import json
import zipfile
import os

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
  #
  if not os.path.exists('templates/themes/theme_name/'):
    # Unzip.
    theme_archive = zipfile.ZipFile('templates/themes/{}.zip'.format(theme_name))
    theme_archive.extractall(path="templates/themes/")
  css_files = []
  js_files = []
  # Restructure directories.
  for root, dirs, files in os.walk("templates/themes/{}".format(theme_name)):
    for file in files:
      if file.endswith(".css") and "bootstrap" not in file:
        css_files.append(os.path.join(root, file))
      elif file.endswith(".js") and "jquery" not in file and "bootstrap" not in file:
        js_files.append(os.path.join(root, file))

  # Read theme files into strings and write to theme files.
  css_data = ""
  for file in css_files:
    with open(file, 'r') as f:
      css_data += f.read()
  js_data = ""
  for file in js_files:
    with open(file, 'r') as f:
      js_data += f.read()

  # Write theme and theme js files.
  with open("applications/{}/static/css/theme.css".format(funnel_app.app_name), "w") as css_theme:
    css_theme.writelines(css_data)
  with open("applications/{}/static/js/theme.js".format(funnel_app.app_name), "w") as js_theme:
    js_theme.writelines(js_data)


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