# coding: utf-8
import datetime
import requests
import os
import urlparse
import xml.sax.saxutils
from lxml import html

from app import app


class Domain(object):

    def __init__(self, url, depth):
        self.url = url
        self.depth = depth
        self.links = [url]
        self.sitemap = None
        self.processed_links = 0

    def get_url(self):
        return self.url

    def get_sitemap(self):
        return self.sitemap

    def get_depth(self):
        return self.depth

    def get_processed_links(self):
        return self.processed_links

    def get_added_links(self):
        return len(self.links)



    def cleaning_links(self, links):
        """
        Returns a list of valid links, excluding links to images.

        links: dict
        Returns: list of links without images
        """
        link_copy = []
        ext = ['jpg', 'css', 'png', 'svg', 'JPG', 'JPEG']
        for s in links:
            sSplit = s.split('/')
            sSplit2 = sSplit[-1].split('.')
            if sSplit2[-1] not in ext:
                link_copy.append(s.replace('/..', ''))
            else:
                continue
        return link_copy


    def getting_links(self):
        """
        Creates a list of links to sitemap

        assigns "Domain" value:
        depth: depth analysis
        processed_links: int, number of parsed links
        links: list
        """
        link_copy = self.links[:]
        depth = self.depth

        while True:
            start_copy = len(self.links)
            for l in link_copy:
                self.processed_links += 1

                link_copy.remove(l)
                print(l)
                response = requests.get(l)
                if 'text/html' not in response.headers['content-type']:
                    break
                parsed_body = html.fromstring(response.text)
                links_page = [urlparse.urljoin(response.url, url) for url in parsed_body.xpath('//a/@href')]

                for link in self.cleaning_links(links_page):
                    if self.url in link and link not in self.links and '#' not in link:
                        masking = xml.sax.saxutils.escape(link)
                        self.links.append(masking)

            link_copy = self.links[start_copy:]
            depth -= 1
            if depth == 0 or len(link_copy) == 0:
                break


    def write_xml_to_sitemap(self):
        """
        Creates a file sitemap.xml

        assigns "Domain" value:
        sitemap: name of the created file
        """
        start ="""<?xml version="1.0" encoding="UTF-8"?>
    <urlset
          xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
                http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">"""
        url_insert ="""
    <url>
        <loc>%s</loc>
    </url>"""
        end = """
    </urlset>
            """
        save_path = os.path.join(app.config['PROJECT_DIR'], 'app/static')


        name_file = str(datetime.datetime.now().strftime("%Y.%m.%d_%H:%M:%S"))+"_sitemap.xml"
        complete_name = os.path.join(save_path, name_file)
        sitemap = open(complete_name, 'w')
        sitemap.write(start)
        for l in self.links:
            sitemap.write(url_insert % l.encode('utf-8'))
        sitemap.write(end)
        sitemap.close()
        self.sitemap = name_file


def make_sitemap(url, depth=3):
    f = Domain(url,depth)
    f.getting_links()
    f.write_xml_to_sitemap()
    return f