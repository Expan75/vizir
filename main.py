import functions_framework
from flask import render_template_string

@functions_framework.http
def hello(request):
	id = request.args.id if request.args.id else None
	if request.method.lower() == "get":
		return render_template_string(f"<h1>Hello html.</h1>")
	else:
		return render_template_string(f"<h3>Thanks, mr postman.</h3>")
