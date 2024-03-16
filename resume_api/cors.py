from django.conf import settings
# from django.http import JsonResponse
# from urllib.parse import urlparse

# from django.http import HttpResponseForbidden

# class CustomCorsMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#         # List of blocked URLs or domains
#         self.blocked_urls = ['/web.postman.co/']
#         self.blocked_domains = ['web.postman.co', 'vercel-3-5-2024.vercel.app']

#     def __call__(self, request):
#         # Check if requested URL is in the blocked list
#         if request.path in self.blocked_urls:
#             return HttpResponseForbidden("Access to this URL is forbidden.")

#         # Check if requested domain is in the blocked list
#         if request.META.get('HTTP_HOST') and request.META.get('HTTP_X_FORWARDED_HOST') in self.blocked_domains:
#             return HttpResponseForbidden("Access from this domain is forbidden.")

#         response = self.get_response(request)
#         return response



    # def __init__(self, get_response):
    #     self.get_response = get_response

    # def __call__(self, request):
    #     allowed_hosts = {"vercel-3-5-2024.vercel.app", "osamaaslam.pythonanywhere.com"}
    #     allowed_user_agents = {"Mozilla", "Chrome", "Safari"}  # Add allowed user agents here
    #     host = request.META.get('HTTP_HOST', '')
    #     user_agent = request.META.get('HTTP_USER_AGENT', '')


    #     if request.META.get('HTTP_X-FORWARDED-HOST'):
    #         response = self.get_response(request)
    #         return response

    #     if host not in allowed_hosts or not any(agent in user_agent for agent in allowed_user_agents):
    #         return HttpResponseForbidden("Access Forbidden")

    #     response = self.get_response(request)
    #     response["Access-Control-Allow-Headers"] = settings.CORS_ALLOW_HEADERS
    #     return response








# class CustomCorsMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Get the requested URL
#         requested_url = request.build_absolute_uri()

#         # Define the allowed origins
#         allowed_origins = {"vercel-3-5-2024.vercel.app", "osamaaslam.pythonanywhere.com"}

#         # Check if the requested URL's origin is allowed
#         parsed_url = urlparse(requested_url)
#         domain = parsed_url.netloc.split(':')[0]  # Extract domain from URL

#         # Extract subdomain (if any)
#         subdomain = domain.split('.')[0] if '.' in domain else None

#         # If the domain/subdomain is not allowed, return error response
#         if domain not in allowed_origins and subdomain not in allowed_origins:
#             return JsonResponse({"error": "Unauthorized origin",
#                                  "origin": domain}, status=403)

#         response = self.get_response(request)

#         # Set allowed origins in the response headers
#         response["Access-Control-Allow-Origin"] = ", ".join(f"https://{origin}" for origin in allowed_origins)
#         response["Access-Control-Allow-Headers"] = settings.CORS_ALLOW_HEADERS

#         return response










# class CustomCorsMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         response = self.get_response(request)

#         # Check the origin header in the request
#         origin = request.headers.get('Origin')
#         requested_url = request.build_absolute_uri()

#         # Define the list of origins to block
#         blocked_origins = ["https://vercel-3-5-2024.vercel.app", "https://web.postman.co"]

#         # If the request origin or requested URL matches the blocked origins
#         if origin in blocked_origins or any(requested_url.startswith(url) for url in blocked_origins):
#             # Block the request by not setting Access-Control-Allow-Origin header
#             response["Access-Control-Allow-Origin"] = "https://www.origin.com"
#         else:
#             # Allow the request with the received origin
#             response["Access-Control-Allow-Origin"] = origin

#         response["Access-Control-Allow-Headers"] = settings.CORS_ALLOW_HEADERS

#         return response


# class CustomCorsMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#         # One-time configuration and initialization.

#     def __call__(self, request):
#         # Code to be executed for each request before
#         # the view (and later middleware) are called.

#         response = self.get_response(request)
#         response["Access-Control-Allow-Origin"] = settings.CORS_ALLOWED_ORIGINS
#         response["Access-Control-Allow-Headers"] = settings.CORS_ALLOW_HEADERS

#         # Code to be executed for each request/response after
#         # the view is called.

#         return response
