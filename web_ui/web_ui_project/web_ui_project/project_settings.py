import os
GOOGLE_CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "data-store-web-ui.json")

# Add pages for navbar here
#   name: app name
#   title: navbar Title
#   url: url template tag link
#
# Pass this to template via context:
# from web_ui_project.project_settings import app_list
# context = {
#         'app_list': app_list,
#     }
#
app_list = [
    {
        'name': "home",
        'title': "",
        'url': "home:index",
    },
    {
        'name': "im1",
        'title': "imGate",
        'url': "im1:index",
    },
    {
        'name': "im2",
        'title': "imGate comparison",
        'url': "im2:index",
    },
    {
        'name': "csv1",
        'title': "CSV",
        'url': "csv1:index",
    },
    {
        'name': "gdrive1",
        'title': "Google Drive",
        'url': "gdrive1:index",
    },
    {
        'name': "log_visual",
        'title': "Log Visualisation",
        'url': "log_visual:index",
    },
]
