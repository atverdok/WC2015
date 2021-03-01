# coding: utf-8
from flask.ext.wtf import Form
from wtforms.fields.html5 import URLField
from wtforms.validators import url

class SitemapForm(Form):
    url = URLField(validators=[url()])
