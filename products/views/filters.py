from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.shortcuts import redirect


@csrf_exempt
def save_filters(request):
    if request.method == "POST":
        data = json.loads(request.body)
        slug = data.pop("slug", None)  
        session_key = f"ui_state:subcategory:{slug}"
        ui_state = request.session.get(session_key, {})
        sort = ui_state.get("sort")
        ui_state = {}
        if sort:
            ui_state["sort"] = sort
        for key, value in data.items():
            if key in ['price_from', 'price_to']:
                ui_state[key] = value
            else:
                if isinstance(value, str):
                    value = [value]
                ui_state[key] = value
        request.session[session_key] = ui_state
        request.session.modified = True
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)


def reset_filters(request, category_slug, subcategory_slug):
    session_key = f"ui_state:subcategory:{subcategory_slug}"
    if session_key in request.session:
        del request.session[session_key]
        request.session.modified = True
    return redirect('products:subcategory_detail', category_slug=category_slug, subcategory_slug=subcategory_slug)

@csrf_exempt
def save_sort(request, key):
    if request.method == "POST":
        data = json.loads(request.body)
        sort_value = data.get("sort")
        slug = data.get("slug")
        session_key = f"ui_state:{key}" + (f":{slug}" if slug else "")
        print(session_key)
        ui_state = request.session.get(session_key, {})
        ui_state["sort"] = sort_value
        request.session[session_key] = ui_state
        request.session.modified = True
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)


@csrf_exempt
def save_tab(request, key):
    if request.method == "POST":
        data = json.loads(request.body)
        slug = data.get("slug")
        tab = data.get("tab")
        session_key = f"ui_state:{key}" + (f":{slug}" if slug else "")
        ui_state = request.session.get(session_key, {})
        ui_state["tab"] = tab
        request.session[session_key] = ui_state
        request.session.modified = True
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)


@csrf_exempt
def save_rating(request):
    if request.method == "POST":
        data = json.loads(request.body)
        slug = data.get("slug")
        rating = data.get("rating")
        session_key = f"ui_state:product:{slug}"
        ui_state = request.session.get(session_key, {})
        if rating is None:
            ui_state.pop("rating", None)
        else:
            ui_state["rating"] = rating
        request.session[session_key] = ui_state
        request.session.modified = True
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)