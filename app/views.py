# coding: utf-8
import requests
from app.make_sitemap import make_sitemap
from flask import render_template, flash, redirect, request, jsonify

from app import app
from forms import SitemapForm


@app.route('/', methods = ['GET', 'POST'])
def index():
    form = SitemapForm()
    if form.validate_on_submit():
        try:
            response = requests.get(form.url.data)
        except:
            error = 'Неверно введен URL адрес, или сайт недоступен.'
            return render_template('index.html',
                error = error.decode('utf-8'),
                form = form)

        f = make_sitemap(form.url.data)

        ans = {}
        ans['url'] = f.get_url()
        ans['sitemap'] = f.get_sitemap()
        ans['depth'] = f.get_depth()
        ans['processed_links'] = f.get_processed_links()
        ans['added_links'] = f.get_added_links()

        return render_template('download.html',
            title = 'download sitemap',
            ans = ans, f = f)

    return render_template('index.html',
        form = form)

