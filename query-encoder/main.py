from flask import render_template, abort
import functions_framework

@functions_framework.http
def index(request):
    if request.method == "POST":
        query = request.form.get("query") # no validation; spooky stuff
        recommendations = [{ "title": f"item{n}" } for n in range(0,50)]
        return render_template(
            "results.html", 
            title="Result | Vizir",
            recommendations=recommendations,
            query=query
        )
    elif request.method == "GET":
        return render_template("landing.html", title="Search | Vizir")
    else:
        abort(404)