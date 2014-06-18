#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Wed Jun 18 15:56:29 BRT 2014
#
 
import urllib2
from xml.dom import minidom
import xml.parsers.expat
import HTMLParser

class URLNotFound(Exception):
    pass

class XMLError(Exception):
    pass

class YGETSUB():
    def __init__(self, idvideo):
        self.idvideo = idvideo

    def getList(self):
        """
        Get a list of availabe subs
        """
        url = 'http://video.google.com/timedtext?type=list&v='+self.idvideo

        # Load URL
        try:
            source = urllib2.urlopen(url).read()
        except urllib2.HTTPError:
            raise URLNotFound('Cant load URL: '+url)

        # Load the XML doc
        try:
            xmlDoc = minidom.parseString(source)
        except xml.parsers.expat.ExpatError:
            raise XMLError('Cant parser XML file.')

        # Create the list of availabe subs
        sublist=[]
        for x in xmlDoc.getElementsByTagName('track'):
            lang_t=x.getAttribute('lang_translated')
            name=x.getAttribute('name')
            lang_code=x.getAttribute('lang_code')
            sublist.append([lang_t, name, lang_code])

        return sublist

    def time2subrip(self, xtime):
        """
        Converts EACH XML time format to SubRip time format
        """

        subtime=[]
        timetxt=''

        if '.' not in xtime: xtime+='.000'

        SEC,MILI=xtime.split('.')
        SEC=int(SEC)

        while len(MILI) < 3:
            MILI=MILI+'0'

        subtime.append(str(SEC/3600))
        subtime.append(str((SEC%3600)/60))
        subtime.append(str((SEC%3600)%60))

        for i in range(3):
            if 1 == len(subtime[i]):
                subtime[i]='0'+subtime[i]

        s=':'.join(subtime)+','+MILI
        return s.encode('utf-8')

    def xml2srt(self, xmlStr):
        """
        Converts a XML file to SubRip time format
        """

        try:
            xmlDoc = minidom.parseString(xmlStr)
        except xml.parsers.expat.ExpatError:
            raise XMLError('Can\'t parser XML file.')

        captionsList = xmlDoc.getElementsByTagName('text') ;

        srtext=''
        for id, x in enumerate(captionsList, 1):
            try:
                caption = x.firstChild.data 
            except AttributeError:
                continue

            # if 'dur' is not present, ValueError is raised.
            start=float(x.getAttribute('start'))
            try:
                dur=float(x.getAttribute('dur'))
            except ValueError:
                dur=0

            end=start+dur

            srtext += str(id) + '\n'
            srtext += self.time2subrip(str(start)) + ' --> ' + self.time2subrip(str(end)) + '\n'
            srtext += HTMLParser.HTMLParser().unescape(caption).encode('utf-8') + '\n'
            srtext += '\n'

        return srtext[:-1]

    def getSub(self, lang_code, name):
        """
        Returns the whole sub as a string.
        lang_code and name are the sub's
        parameters.
        """

        name=urllib2.quote(name)
        url = 'http://video.google.com/timedtext?type=track&v='+self.idvideo
        url = url + '&lang='+lang_code+'&name='+name

        try:
            xmlSrt = urllib2.urlopen(url).read()
        except urllib2.HTTPError:
            raise URLNotFound('Can\'t load URL: '+url)

        return self.xml2srt(xmlSrt)

# Example how to use the YGETSUB class. Here you
# can pass the video code as the first parameter
# (eg: kGYACultjCY) and the output file as the
# second parameter
if __name__ == '__main__':
    import sys

    argc = len(sys.argv)
    if argc < 3:
        print '[use]',sys.argv[0],'<video code> <output>'
        sys.exit(-1)

    idvideo = sys.argv[1]
    outputfile = sys.argv[2]

    subobj = YGETSUB(idvideo)

    try:
        # Get the sub list
        sublist = subobj.getList()
    except URLNotFound:
        print 'Error: Invalid video code'
        sys.exit(-1)
    except XMLError:
        print 'Error: This video does not have any subtitles.'
        sys.exit(-1)

    # Show a simply menu to select the correct sub
    print 'Select the idiom (hit ENTER to exit)'
    print sublist
    l = len(sublist)
    for c, [label, name, idlang] in enumerate(sublist):
        print '[',c,']',label

    opt = raw_input('>> ') 

    if opt :
        opt = int(opt)
        if opt < len(sublist):
           try:
              filefd=open(outputfile, 'w')
           except:
               print 'Error: Can\'t write to ', outputfile
               sys.exit(-1)
           else:
               label, name, idlang = sublist[opt]
               filefd.write(subobj.getSub(idlang, name))
           finally:
               filefd.close()
