#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2013 Jordi Mas i Hernandez <jmas@softcatala.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import sys
sys.path.append('../../src/')

import polib
import time
import os
from whoosh.fields import *
from whoosh.index import create_in
from whoosh.analysis import StandardAnalyzer
from jsonbackend import JsonBackend
from optparse import OptionParser

po_directory = None

class Search:

    dir_name = "indexdir"
    writer = None
    words = 0
    projects = 0

    def process_projects(self, po_directory):

        json = JsonBackend("../../src/projects.json")
        json.load()

        for project_dto in json.projects:
            self._process_project(po_directory, project_dto.name, 
                                  project_dto.filename)
            self.projects = self.projects + 1
            
        self.write_statistics()
            
    def write_statistics(self):

        today = datetime.date.today()
        html = u'<p>L\'índex va ser actualitzat per últim cop el ' + today.strftime("%d/%m/%Y")
        html += u' i conté ' + str(self.projects) + ' projectes amb un total de ' 
        html += format(str(self.words), '.d') + ' paraules</p>'
        html_file = open("statistics.html", "w")
        html_file.write(html.encode('utf-8'))        
        html_file.close()

    def _process_project(self, po_directory, name, filename):

        full_filename = os.path.join(po_directory, filename)
        print "Processing: " + full_filename
        
        try:
            input_po = polib.pofile(full_filename)
            
            for entry in input_po:
                s = unicode(entry.msgid)
                t = unicode(entry.msgstr)
                c = unicode(entry.comment)
                p = unicode(name)
                
                string_words = entry.msgstr.split(' ')
                self.words += len(string_words)
                self.writer.add_document(source=s, target=t, comment=c, project=p)

        except Exception as detail:
            print "Exception: " +  str(detail)


    def create_index(self):
    
        MIN_WORDSIZE_TO_IDX = 1

        schema = Schema(source=TEXT(stored=True), target=TEXT(stored=True,
                        analyzer=StandardAnalyzer(minsize=MIN_WORDSIZE_TO_IDX)),
                        comment=TEXT(stored=True), project=TEXT(stored=True))
                        
        if not os.path.exists(self.dir_name):
            os.mkdir(self.dir_name)

        ix = create_in(self.dir_name, schema)
        self.writer = ix.writer()
        
def read_parameters():

    global po_directory

    parser = OptionParser()

    parser.add_option("-d", "--directory",
                      action="store", type="string", dest="po_directory",
                      default="../../latest-memories/po/",
                      help="Directory to find the PO files")

    (options, args) = parser.parse_args()

    po_directory = options.po_directory
    

def main():
    '''
        Given a PO file, enumerates all the strings, and creates a Whoosh
        index to be able to search later
    '''

    print "Create Whoosh index from a PO file"
    print "Use --help for assistance"

    start_time = time.time()
    
    read_parameters()
    search = Search()
    search.create_index()
    search.process_projects(po_directory)
    search.writer.commit()
    
    end_time = time.time() - start_time
    print "time used to create the index: " + str(end_time)

if __name__ == "__main__":
    main()
