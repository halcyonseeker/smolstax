#!/usr/bin/env python
# smolstax.py: A minimal web frontend for openstax.org textbooks
#     Website: https://smolstax.lagrangian.space
#     License: GPL
#      Author: Thalia Wright <thalia@lagrangian.space>
#      Source: https://git.sr.ht/~thalia/smolstax

import sys
import requests
import json
import os

#
# Helper Functions
#
def die(code: int, msg: str):
    """ Assemble a HTML error page and exit """
    head = "<html><head><meta charset='UTF-8'> <title>ERROR</title></head><body>\n"
    body = "<h1>Error: " + str(code) + "</h1><hr><h2>" + msg + "</h2>\n"
    foot = "</body></html>\n"
    print(head + body + foot)
    sys.exit(1)
    
def open_index():
    """ Open or download the index.json file containing info about the books """
    index_file = open("index.json")
    # try:
    #     f.seek(2)
    # except:
    #     r = requests.get("https://openstax.org/apps/cms/api/v2/pages/30/")
    #     # print("open_index: ", r.text)
    #     if r.status_code != 200:
    #         die(500, "Failed to download index file from openstax.org")
    #     try:    
    #         index_file.write(r.text)
    #     except io.UnsupportedOperation:
    #         die(500, "Failed to write to index.json")
    # print("DBG: open_index:")
    # print(str(index_file.read()))
    
    return str(index_file.read())

def open_bookinfo(idnum: str):
    """ Open or fetch a json file containing information about this book """
    bookinfo = open(idnum + ".json")
    # try:
    #     f.seek(2)
    # except:
    #     api_url = "https://openstax.org/apps/cms/api/v2/pages/"
    #     r = requests.get(api_url + str(self.idnum))
    #     if r.status_code != 200:
    #         die(500, "Failed to download book info file from openstax.org")
    #     try:
    #         bookinfo.write(r.text)
    #     except io.UnsupportedOperation:
    #         die(500, "Failed to write book info file " + str(self.idnum) + ".json")
    # print("DBG: __open_bookinfo:")
    # print(str(bookinfo.read()))

    return str(bookinfo.read())

#
# Classes
#
class Book:
    """ Each textbook in the Openstax library is represented by a Book object """
    title     = "NA"            # The book title
    idnum     = -999            # The book's id number
    slug      = "NA"            # The book's name in urls
    last_date = "NA"            # Date last updated
    cover_url = "NA"            # The book's cover url
    pdf_url   = "NA"            # The books's pdf url
    html_url  = "NA"            # The full book's local html url
    toc_url   = "NA"            # The book's local ToC url
    subjects  = ["all"]

    def gen_html_summary(self):
        """ Generate the book's table of contents and description as HTML"""
        info = json.loads(open_bookinfo(str(self.idnum)))

        head = "<html><head><meta charset='UTF-8'> <title>" + self.title + "</title></head><body>\n"
        body = "<h1>" + self.title + "</h1><hr>\n"
        desc = "<h2>Summary</h2><br>\n"
        toc  = "<h2>Table of Contents</h2><br>\n"
        foot = "</body></html>\n"
        desc += info['description']
        toc  += "<ol>\n"
        for chapter in info['table_of_contents']['contents']:
            chptr_title = chapter['title']
            chptr_slug  = chapter['slug']
            chptr_url   = self.slug + "/pages/" + chptr_slug
            chptr_link  = "<li><a href='" + chptr_url + "'>" + chptr_title + "</a></li>\n"
            toc        += chptr_link
            if 'contents' in chapter:
                toc += "<ol>\n"
                for section in chapter['contents']:
                    sctn_title = section['title']
                    sctn_slug  = section['slug']
                    sctn_url   = self.slug + "/pages/" + sctn_slug
                    sctn_link  = "<li><a href='" + sctn_url + "'>" + sctn_title + "</a></li>\n"
                    toc       += sctn_link
                toc += "</ol>\n"
        toc += "</ol>\n"
        return head + body + desc + toc + foot

    def gen_html_chapter_section(self, section):
        """ Generate a section of a chapter as HTML """
        # TODO: for json prototyping, remove this later
        # TODO: figure out how section ids work
        r = requests.get("https://openstax.org/contents/f0fa90be-fca8-43c9-9aad-715c0a2cee2b@9.1:06a5799f-762d-4f1f-8603-b077f4284a43.json")
        text = json.loads(r.text)
        content = text['content']
        return content


    def gen_html_long(self):
        """ Generate the full book as HTML """
        # TODO figure out how sections work, iterate over them and assemble a page

class Library:
    """ Openstax's collection of textbooks is represented by a Library object """
    books = []

    def __init__(self, index_file: str):
        """ Build a list of OpenStax textbooks from the json object index"""
        index = json.loads(index_file)
        for p in range(len(index['books'])):
            book = Book()
            book.title     = index['books'][p]['title']
            book.idnum     = index['books'][p]['id']
            book.slug      = index['books'][p]['slug']
            book.last_date = index['books'][p]['last_updated_pdf']
            book.cover_url = index['books'][p]['cover_url']
            book.pdf_url   = index['books'][p]['high_resolution_pdf_url']
            book.toc_url   = index['books'][p]['slug']
            # TODO ^^^ Build TOC URL
            for s in index['books'][p]['subjects']:
                book.subjects.append(s)
            self.books.append(book)

    def gen_html_index(self, subject):
        """ Generate a list of OpenStax textbooks by subject as HTML """
        head = "<html><head><meta charset='UTF-8>'> <title>SmolStax Index</title></head><body>\n"
        body = head + "<h1>Index of SmolStax Textbooks</h1><hr>\n"
        foot = "</body></html>\n"
        body += "<h2>Index of " + subject + "</h2>"
        for b in self.books:
            if subject in b.subjects:
                body += "<div class='entry' id='" + b.slug + "'>\n"
                body += "<h2>" + b.title + "</h2>\n"
                body += "<b>Last Updated: </b>" + str(b.last_date) + "<br>\n"
                body += "<a href='" + b.toc_url + "'>Table of Contents</a><br>\n"
                body += "<a href='" + str(b.pdf_url) + "'>Read as PDF</a><br>\n"
                body += "<a href='https://openstax.org/details/" + b.slug + "'>Read on OpenStax</a>\n"
                body += "<hr></div>\n"
            else:
                body += "<br><h2>Invalid subject</h2>"
        return head + body + foot

    def find_slug(self, slug):
        """ Return the book that corresponds to slug """
        return [b for b in self.books if b.slug == slug]


#
# Main function
#
def cgi_main(argv):
    """ Main function when running as a cgi script. argv is usually sys.argv"""
    if len(argv) != 2:
        print("EXAMPLE ARGUMENTS:")
        print("  /subjects/all -- TODO: support other subjects")
        print("  /details/prealgebra-2e")
        print("  /books/prealgebra-2e/pages/1-introduction -- TODO: learn api")
        return 1

    if argv[1].split("/")[1] == "subjects":
        # Book listings
        # /subjects/(all|science|...|...|...|...|college-success|high-school)
        try:
            subject = argv[1].split("/")[2]
        except:
            die(404, "Command-line argument was not a valid path.")
        library = Library(open_index())
        print(library.gen_html_index(subject))
        return 0
        
    elif argv[1].split("/")[1] == "details":
        # Summary page
        # /details/slug (eg, /details/books/prealgebra-2e)
        try:
            slug = argv[1].split("/")[2] + "/" + argv[1].split("/")[3]
        except:
            die(404, "Command-line argument was not a valid path.")
        library = Library(open_index())
        print(library.find_slug(slug)[0].gen_html_summary())
        return 0

    elif argv[1].split("/")[1] == "books":
        print("Chapter: " + argv[1].split("/")[4])
        # Book chapters
        # /book_slug/pages/chapter_slug (eg, /books/prealgebra-2e/pages/1-introduction)
    else:
        print("404");
            
    return 0

if __name__ == "__main__":
    sys.exit(cgi_main(sys.argv))
