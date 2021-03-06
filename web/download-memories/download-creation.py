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
from jsonbackend import JsonBackend
import os
import datetime
from polib import pofile
from optparse import OptionParser

po_directory = None
tmx_directory = None
out_directory = None


def link(text, link):
    html = '<a href="' + link + '">'
    html += text + '</a>'
    return html
    
    
def table_row_generate(name, projectweb, potext, pofile, tmxtext, tmxfile):

    words = get_statistics(potext)
    if (words == 0):
        print "Skipping empty translation memory: " + potext
        return ''
    
    date = get_file_date(potext)
    html = "<tr>\r"
    if (len(projectweb) > 0):
        html += "<td><a href='" + projectweb + "'>"  + name + "</a></td>\r"
    else:
        html += "<td>" + name + "</td>\r"

    html += "<td>" + link(get_zip_file(potext), pofile) + "</td>\r"
    html += "<td>" + link(get_zip_file(tmxtext), tmxfile) + "</td>\r"
    html += "<td>" + format(str(words), '.d') + "</td>\r"
    html += "<td>" + date + "</td>\r"
    html += "</tr>\r"
    return html

def get_subdir():

    return "memories/"
    
def get_path_to_po(po_file):

    return os.path.join(get_subdir(), po_file)

def get_path_to_tmx(po_file):

    filename, file_extension = os.path.splitext(po_file)
    tmxfile = filename + ".tmx"
    return os.path.join(get_subdir(), tmxfile)
    
def get_tmx_file(po_file):

    filename, file_extension = os.path.splitext(po_file)
    tmxfile = filename + ".tmx"
    return tmxfile

def get_zip_file(filename):

    return filename + ".zip"
    
def table_row(name, projectweb, potext):

    return table_row_generate(name, projectweb, potext,
                              get_zip_file(get_path_to_po(potext)),
                              get_tmx_file(potext),
                              get_zip_file(get_path_to_tmx(potext)))
                              
def get_file_date(filename):

    full_path = os.path.join(po_directory, filename)
    last_ctime = datetime.date.fromtimestamp(os.path.getctime(full_path))
    last_date = last_ctime.strftime("%d/%m/%Y")
    return last_date

def process_projects():

    json = JsonBackend("../../src/projects.json")
    json.load()

    html = u'<h1 class ="section">Baixa les memòries de traducció</h1>\r'
    html += u'<p>Baixeu les memòries de traducció per poder-les configurar al vostre programa de traducció habitual.</p>\r'
    html += u'<p>Disposem instruccions de com fer-ho '
    html += u'<a href="http://www.softcatala.org/wiki/Configurar_PoEdit_amb_mem%C3%B2ries_de_traducci%C3%B3">pas a pas</a> '
    html += u'amb l\'eina de traducció PoEdit.</p>\r'
    html += '<table border="1" cellpadding="5px" cellspacing="5px" style="border-collapse:collapse;">\r'
    html += '<tr>\r'
    html += '<th>Projecte</th>\r'
    html += '<th>Fitxer PO</th>\r'
    html += '<th>Fitxer TMX</th>\r'
    html += u'<th>Paraules traduïdes</th>\r'
    html += u'<th>Última actualització</th>\r'
    html += '</tr>\r'
    
    memories = {u'Totes les memòries de tots els projectes' : 'tm.po',
        u'Totes les memòries de projectes de Softcatalà': 'softcatala-tm.po'}
    
    for name, filename in memories.items():
        html += table_row(name, '', filename)
        create_zipfile(po_directory, filename)
        create_zipfile(tmx_directory, get_tmx_file(filename))
    
    projects = sorted(json.projects, key=lambda x: x.name.lower())
    for project_dto in projects:
        if (project_dto.name != 'Header'):
        
            create_zipfile(po_directory, project_dto.filename)
            create_zipfile(tmx_directory, get_tmx_file(project_dto.filename))
            
            html += table_row(project_dto.name, project_dto.projectweb,
                              project_dto.filename)

    html += '</table>\r'
    today = datetime.date.today()
    html += '<br>\r'
    html += u'Data de generació d\'aquesta pàgina: ' + today.strftime("%d/%m/%Y")
    html += '<br>\r'
    return html
    
def create_zipfile(src_directory, filename):

    srcfile = os.path.join(src_directory, filename)
    zipfile = os.path.join(out_directory,  get_subdir(), get_zip_file(filename))
    
    if not os.path.exists(srcfile):
        print "Cannot zip:" + srcfile
        return

    cmd = 'zip -j {0} {1}'.format(zipfile, srcfile)
    print cmd
    os.system(cmd)


def get_statistics(filename):

    words = 0

    try:
    
        full_path = os.path.join(po_directory, filename)
        poFile = pofile(full_path)
        print "Getting stats for: " + full_path
        
        for entry in poFile:
            string_words = entry.msgstr.split(' ')
            words += len(string_words)

    except Exception as detail:
        print("Statistics exception " + filename)
        print(detail)
        
    finally:
        return words

def read_parameters():

    global po_directory
    global tmx_directory
    global out_directory

    parser = OptionParser()

    parser.add_option("-d", "--podir",
                      action="store", type="string", dest="po_directory",
                      default="../../latest-memories/po/",
                      help="Directory to find the PO files")

    parser.add_option("-t", "--tmxdir",
                      action="store", type="string", dest="tmx_directory",
                      default="../../latest-memories/tmx/",
                      help="Directory to find the TMX files")
                      
    parser.add_option("-o", "--ouputdir",
                      action="store", type="string", dest="out_directory",
                      default="",
                      help="Directory to output the files")

    (options, args) = parser.parse_args()

    po_directory = options.po_directory
    tmx_directory = options.tmx_directory
    out_directory = options.out_directory

def create_output_dir(subdirectory):

    directory = os.path.join(out_directory, subdirectory)
    if not os.path.exists(directory):
        os.mkdir(directory)
        

def main():
    '''
        Reads the projects and generates an HTML to enable downloading all
        the translation memories
    '''

    print "Creates download.html file"
    print "Use --help for assistance"

    read_parameters()
    
    create_output_dir("memories")
   
    download = os.path.join(out_directory, "download.html")
    html = process_projects()
    html_file = open(download, "w")
    html_file.write(html.encode('utf-8'))
    html_file.close()

if __name__ == "__main__":
    main()
