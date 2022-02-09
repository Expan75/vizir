from flask import render_template
import functions_framework

@functions_framework.http
def index(request):
		return render_template("landing.html", title="Vizir Home")