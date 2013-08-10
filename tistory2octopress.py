#!/usr/bin/env python
# -*- encoding:utf8 -*-

import urllib, sys, re, tarfile, os, random
from datetime import datetime
from lxml import etree
from unidecode import unidecode

files = []
random_str = str(random.random())[2:6]
attachment_dir = 'attachment' + random_str + '/'
    
def parseFile(str):
    return etree.XML(str)

def getNodes(xml, tag):
    return xml.findall(tag)

def getNode(xml, tag):
    return xml.find(tag)

def getString(xml):
    return etree.tostring(xml, method='text', encoding='utf-8')

def getContent(xml, tag):
    if tag is 'category' and getNode(xml, tag) is None:
        return ''
    else:
        return getString(getNode(xml, tag))

def getFileName(time, title):
    timestamp = datetime.fromtimestamp(int(time)).strftime('%Y-%m-%d')
    return '%s-post-%s.markdown' % (timestamp, title)

def handlingContent(str, img_str):
    return re.sub(r'\[##.+?##\]', img_str, str) 

def makeFile(xml):
    info = {}
    info['layout'] = 'layout: %s\n' % 'post'
    info['title'] = 'title: "%s"\n' % getContent(xml, 'title')
    info['date'] = 'date: %s\n' % datetime.fromtimestamp(int(getContent(xml, 'published'))).strftime('%Y-%m-%d %H:%M:%m')
    info['comments'] = 'comments: %s\n' % 'true'
    info['external'] = 'external-url: %s\n' % ''
    info['categories'] = 'categories: %s\n' % getContent(xml, 'category')
    info['sharing'] = 'sharing: %s\n' % 'false'
    
    content_str = makeImage(getNodes(xml, 'attachment'), getContent(xml, 'content'))

    filename = re.sub(r' ', '_', unidecode(getFileName(getContent(xml, 'published'), getContent(xml, 'title')).decode('utf-8')))
    files.append('_posts/' + filename)
    f = open('_posts/' + filename, 'w')
    f.write('---\n')
    f.write(''.join([ i for i in info.itervalues()]))
    f.write('---\n')
    f.write(content_str)
    f.close()
    return False

def makeImage(xml, content_str):
    content = content_str 
    for node in xml:
        name = getContent(node, 'name')
        width = node.attrib['width']
        height = node.attrib['height']
        alt = getContent(node, 'label')
        content_base64 = getContent(node, 'content')

        image_str = '{%% img %s %s %s %s %%}' % ('/images/' + name, width, height, alt) 
    
        content = handlingContent(content, image_str)

        files.append('images/' + name)
        image = open('images/' + name, 'wb')
        image.write(content_base64.decode('base64'))
        image.close()

    return content 

def getCategory(xml):
    categories = []
    for node in getNodes(xml, 'category'):
        categories.append(getContent(node, 'name'))
    return categories

def compress(files):
    compressed_file = tarfile.open(datetime.now().strftime('%Y-%m-%d') + '.tar', 'w')
    for file in files:
        compressed_file.add(file)
    compressed_file.close()
    return False    

def delete_files(files):
    for file in files:
        if os.access(file, os.R_OK):
            os.remove(file)

def main(filename):
    xml = parseFile(open(filename).read())
    post_dir = os.access('_posts', os.F_OK)
    img_dir = os.access('images', os.F_OK)
        
    if post_dir == False:
        os.mkdir('_posts')
    if img_dir == False:
        os.mkdir('images')

    for node in getNodes(xml, 'post'):
        if getContent(node, 'visibility') == 'public':
            makeFile(node)
    compress(files)
    delete_files(files)

    if post_dir == False:
        os.rmdir('_posts')
    if img_dir == False:
        os.rmdir('images')



if __name__ == '__main__':
    main(sys.argv[1])
   
