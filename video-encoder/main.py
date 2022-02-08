import functions_framework

@functions_framework.http
def hello(request):
	return "hello query encoder!"
