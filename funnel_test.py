import funnel
from threading import Thread

if __name__ == "__main__":
  company_name = raw_input("Company Name:")
  if len(company_name) == 0:
    company_name = "Clearline Industries"
  logo_url = raw_input("Logo url:")
  if len(logo_url) == 0:
    logo_url = "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"
    #Clearline http://i.imgur.com/wc0nX3r.png
  pages = ["About", "Services", "Team"]
  email = "junk@data.com"
  google_analytics = "JUNKDATA"
  generator = funnel.Funnel(company_name, logo_url, pages, email, google_analytics)
  generator.generate_app()
  background_server = Thread(target=generator.start_app)
  background_server.start()
  while True:
    theme = raw_input("Theme:").lower().strip() + ".css"
    generator.change_theme(theme)