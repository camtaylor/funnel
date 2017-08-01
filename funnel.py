import os
import jinja2


def create_page(app_name, page):
  os.system("cp templates/flask/templates/page.html applications/{}/templates/{}.html".format(app_name, page))
   
if __name__ == "__main__":

  environment = jinja2.Environment(loader=jinja2.FileSystemLoader('templates/flask'))
  app_name = raw_input("Company name:").replace(" ", "_")
  logo = raw_input("Logo url:")
  pages = raw_input("Page names separated by comma:").lower().split(",") 
  email = raw_input("Companies email address:")
  google_analytics = raw_input("Google analytics customer id:")
  

  # Create app directories
  os.system("mkdir applications/{}".format(app_name))
  #Get app template
  template = environment.get_template('app.py')
  # Create app.py
  with open("applications/{}/app.py".format(app_name),"w") as f:
    f.write(template.render(pages=pages))
  # Create template directory
  os.system("mkdir -p applications/{}/templates".format(app_name)) 
  # Create base template 
  with open("applications/{}/templates/base.html".format(app_name), "w") as f:
    template = environment.get_template("templates/base.html")
    f.write(template.render(logo=logo,pages=pages))
  # Create page templates
  create_page(app_name, "home")
  for page in pages: 
    create_page(app_name, page)
  os.system("python applications/{}/app.py".format(app_name))
