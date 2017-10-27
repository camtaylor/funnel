from flask import Flask, request, render_template

app = Flask(__name__, static_url_path='/static')

@app.route("/", methods=["GET"])
def home():
  return render_template("home.html")

@app.route("/about", methods=["GET"])
def about():
  return render_template("about.html")

@app.route("/services", methods=["GET"])
def services():
  return render_template("services.html")

@app.route("/patient_stories", methods=["GET"])
def patient_stories():
  return render_template("patient_stories.html")

@app.route("/faqs", methods=["GET"])
def faqs():
  return render_template("faqs.html")

@app.route("/contact", methods=["GET"])
def contact():
  return render_template("contact.html")

if __name__ == "__main__":
  app.run()