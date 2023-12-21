from django.shortcuts import redirect, HttpResponseRedirect, HttpResponse


def is_logged_in(func):
    """
    This function is used to check if the user is logged in or not.
    """

    def wrapper(request, *args, **kwargs):
        uid = request.header.get("uid")
        if uid is not None:
            return func(request, *args, **kwargs)
        else:
            return HttpResponse("You are not logged in!")

    return wrapper
