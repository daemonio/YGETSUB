YGETSUB
=======

A simple python script to download youtube subtitles. Also, it converts XML time format to SubRip time format.

Examples
========

Just pass the video code and the output file:

<pre>
$ ./YGETSUB.py kGYACultjCY my_subtitle.srt
</pre>

you will be asked the select the idiom of the subtitle. After this, it will be saved in my_subtitle.srt

XML To SRT (SubRip) Conversion
==============================

You can also use this to convert a file in XML time format to SubRip time format:

<pre>
from YGETSUB import YGETSUB

xmlfile = open('timedtext.xml', 'r')

sub = YGETSUB('') # just pass any ID, actually
print sub.xml2srt(xmlfile.read())
</pre>

