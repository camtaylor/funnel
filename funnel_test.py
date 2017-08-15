import funnel
from threading import Thread

if __name__ == "__main__":
  app_name = raw_input("Company Name:")
  if len(app_name) == 0:
    app_name = "Example Company"
  logo_url = raw_input("Logo url:")
  if len(logo_url) == 0:
    logo_url = "http://i.imgur.com/wc0nX3r.png"
    #Clearline http://i.imgur.com/wc0nX3r.png
  page_names = raw_input("Page names separate by comma:")
  pages = [page.strip() for page in page_names.split(",")]
  if len(pages) == 0:
    pages = ["a","b","c"]
  email = "junk@data.com"
  google_analytics = "JUNKDATA"
  generator = funnel.Funnel(app_name, logo_url, pages, email, google_analytics)
  generator.generate_app()
  generator.setup_heroku()
  generator.export_app()
  background_server = Thread(target=generator.start_app)
  background_server.start()
  while True:
    theme = raw_input("Theme:").lower().strip() + ".css"
    generator.change_css_theme(theme)