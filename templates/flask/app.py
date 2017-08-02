from flask import Flask, request, render_template

app = Flask(__name__, static_url_path='/static')

@app.route("/", methods=["GET"])
def home():
  return render_template("home.html")
{% for page in pages %}
@app.route("/{{page}}", methods=["GET"])
def {{page}}():
  return render_template("{{page}}.html")
{% endfor %}
@app.route("/contact", methods=["GET"])
def contact():
  return render_template("contact.html")

if __name__ == "__main__":
  app.run()