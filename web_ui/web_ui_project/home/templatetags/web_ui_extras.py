from django.template.defaulttags import register


@register.filter
def get_title(app_list, app_name):
    app = next((l for l in app_list if l['name'] == app_name), None)
    if app and 'title' in app:
        return app['title']
    else:
        return "templatetags: error: title not found"
