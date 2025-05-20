from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="static/templates")

def get_templates():
    return templates
