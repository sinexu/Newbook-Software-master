#!/usr/bin/env python3.2
# autotagger web interface
#

import cgi
import cgitb; cgitb.enable()
import autotagger
import codecs
import sys
import os
import time
import glob
from random import randint
from distutils.dir_util import remove_tree

import datetime


WEBPAGES = [] #list of all webpages, start h2+
HTTP_HEADERS = "Content-type: text/html\nSet-cookie: session=%(cookie)s"
#leaves html and body tags open
TEMPLATE = """
<!doctype html>
<html>
<head>
	<link href="http://depts.washington.edu/ndth/newbook4.css" type="text/css" rel="stylesheet"></link>
	<title>Svoboda Diaries Project Autotagger</title>
	<link type="image/x-icon" href="http://depts.washington.edu/ndth/images/favicon.ico" rel="shortcut icon"></link>
	<link type="image/x-icon" href="http://depts.washington.edu/ndth/images/favicon.ico" rel="icon"></link>
	<link type="text/css" rel="stylesheet" href="http://fonts.googleapis.com/css?family=Open+Sans"></link>
  <!-- <script src="http://depts.washington.edu/ndth/svoboda.js" type="text/javascript"></script> -->
  <meta charset="UTF-8"></meta>
  <style type="text/css">
  .filetype {display: none;}
  </style>
  <script src="welcome.js"></script>
</head>
<body>
<div id="header">
	<div id="logo"><a href="http://depts.washington.edu/ndth/"><img alt="logo" src="http://depts.washington.edu/ndth/images/nbdt_logo_216px.png"></img></a></div>
	<div id="top_right">
  <span>Inspiration starts here.</span>
  <a href="http://facebook.com/pages/Svoboda-Diary-Project/381133915236500"><img alt="Facebook" src="http://depts.washington.edu/ndth/images/facebook_small.gif"></img></a><a href="http://twitter.com/SvobodaDiaries"><img alt="Twitter" src="http://depts.washington.edu/ndth/images/twitter_small.gif"></img></a></div>
	<div id="panel"><hr></hr><a href="http://depts.washington.edu/svobodad/"><img alt="" src="http://depts.washington.edu/ndth/images/banner2.jpg"></img></a></div>
</div>  
"""


ERROR_PAGE = """
    <h3>Errors in the input, they are listed below</h3>
    <p>
 <form action="index.cgi" method="post"
          enctype="multipart/form-data">
 <input type="submit" name="" value="Upload another transcription file"/>
 <input type="file" name="sdtf" /></p>
    %(errors)s
</form>
</body>
</html>"""
WEBPAGES.append(ERROR_PAGE)


SUCCESS_PAGE = """
<h2>Autotagger Success!</h2>
<style>
%(css)s
</style>
<body>
<h3>Your %(filetype)s is ready!</h3>
<h4>%(timestamp)s</h4>

<p>Your TEI-XML result is here: <a href="%(teioutfile)s">here</a>
(right click the link to save the file to your computer).</p>
<ul>
  <li>
  <form action="index.cgi" method="post" enctype=multipart/form-data">
    <input type="hidden" name="html" value="on"/>
    <span id="html_span">Process your TEI-XML to generate an HTML file:</span> 
    <input id="html_but" type="submit" value="Go!"/>
    %(htmloutfile)s
  </form>
  </li>
  <li>
  <form action="index.cgi" method="post" enctype=multipart/form-data">
    <input type="hidden" name="tex" value="on"/>
    <span id="latex_span">Process your TEI-XML to generate a LaTeX file:</span> 
    <input id="latex_but" type="submit" value="Go!"/>
    %(texoutfile)s
  </form>
  </li>
  <li>Try again with another transcription format file (clears your sessions 
      directory, download any files you want to keep first!)
   <form action="index.cgi" method="post" enctype="multipart/form-data">
     <input type="file" name="sdtf" required/> <input type="submit" value="Upload transcription file"/>
   </form>
  </li>
</ul>

<h4>other options (coming soon):</h4>
<ul>
  <li>Validate: check that you're TEI-XML output is valid</li>
  <li>Configuration options for the autotagging process</li>
</ul>
</body>
</html>"""
WEBPAGES.append(SUCCESS_PAGE)

WELCOME_PAGE = """
<h2>Newbook Autotagger Online Interface</h2>

<div id=content>
<p><strong>Please choose file type you will upload:</strong></p>
<input class="uploadfile" type="radio" name="file" value="SDTF" onchange="filetype_chosen()">
SDTF (svoboda diaries transcription format)
<input class="uploadfile" type="radio" name="file" value="teixml" onchange="filetype_chosen()"//>
teixml
<div class="inputfile" id="SDTFfile" style="display: block;">
      <p>Submit a SDTF file (svoboda diaries transcription format);
         we'll run the autotagger and show you to the result.
      </p>
      <form action="autotagger.cgi" method="post"
         enctype="multipart/form-data">
         <input type="file" name="sdtf" required/></p>
           <p> Provide optional configuration information below:</p>
         <p></p>
         <fieldset>
            <legend>Header Information:</legend>
            <ul>
               <p><span>Insert Document Title Here: <input type="text" name="TITLE" /></span></p>
               <p><span>Insert Author Name Here: <input type="text" name="AUTHOR" /></span></p>
               <p><span>Insert Copyright Data Here: <input type ="text" name = "COPYRIGHT" /></span></p>
               <p><span>Insert Distributor Name Here: <input type ="text" name = "DISTRIBUTOR" /></span></p>
               <p><span>Insert Date Here: (MM/DD/YYYY): <input type ="datetime" name = "DATE" /></span></p>
               <p><span>Insert Your Type Here: <input type="text" name="ID_TYPE" /></span></p>
               <p><span>Insert ID Number Here: <input type="text" name="ID_VALUE" /></span></p>
               <p><span>Enter Bibliographical Information Here: <input type ="text" name = "BIBL_INFO" /></span></p>
               <p><span>Insert Date of Last Edit (MM/DD/YYYY): <input type = "datetime" name = "DATE_LAST_UPDATED" /></span></p>
               <p><span>Insert Name of Project Responsible for Transcription: <input type = "text" name = "RESP_PROJECT" /></span></p>
               <p><span>Insert Name of Project Lead: <input type = "text" name = "PROJECT_LEAD" /></span></p>
               <p><span>Insert Project Here: <input type = "text" name = "PROJECT_DESC" /></span></p>
            </ul>
         </fieldset>
<br />
         <fieldset>
            <legend>Document Information:</legend>
            <ul>
               <p><span>Do you want section title in text? 
                  <input type = "radio" name="SECTION_IN_TEXT" value="True">Yes 
                  <input type = "radio" name="SECTION_IN_TEXT" value="False">No</span>
               </p>
               <p><span>How many divisions do you prefer?
                  <input type = "radio" name="NUMBER_OF_DIVS" value="1">1
                  <input type = "radio" name="NUMBER_OF_DIVS" value="2">2</span>
               </p>
               <p><span>Do you want subsection title in text?
                  <input type = "radio" name="SUBSECTION_IN_TEXT" value="Treu">Yes
                  <input type = "radio" name="SUBSECTION_IN_TEXT" value="False">No</span>
               </p>
               <p><span>Do you want to include line breaks?
                  <input type = "radio" name="LINE_BREAKS" value="Yes">Yes
                  <input type = "radio" name="LINE_BREAKS" value="No">No</span>
               </p>
            </ul>

      <p><input type = "submit" value="Upload transcription file"/></p>
      </form>
      </fieldset>
<br />
</div>
<div class="inputfile" id="teixmlfile" style="display: none;">
    <p>Submit a teixml file;
       we'll run the xslt scripts and show you to the result.
    </p>
    <form action="autotagger.cgi" method="post"
         enctype="multipart/form-data">
         <input type="file" name="tex" required/>
         <p><input type = "submit" value="Upload XML file"/></p>
    </form>
</div>





Our code is open-source access our repository <a href="https://github.com/kch349/Newbook-Software">here</a>.
</div>
<div id=content> <h3> The Autotagger </h3>
	<p> This autotagger assumes that that the file passed into it is properly marked up according to the Svoboda Diaries Transcription Format. You may transcribe anything using this unique transcription format to generate XML, HTML, LaTeX or PDF documents.</p>
  <h3> About The Transcription Format </h3>
  <p> Stuff about transcribing.  Maybe examples.  Make new page? </p>
  <h3> Coming Soon.... </h3>
  <h3> Download some files </h3>
  <ul>
    <li><a href="download.html">Download page</a></li>
  </ul>
  <p> Stay tuned for configuration and customization options. </p>
<div id="footer"><hr></hr>  
		Copyright © 2013 Newbook Digital Text in the Humanities. All Rights Reserved.
    <br></br><a href="http://www.washington.edu/online/privacy"><strong>PRIVACY</strong></a>
       | 
    <a href="http://www.washington.edu/online/terms"><strong>TERMS</strong></a>
</div>
</body>
</html>
"""
WEBPAGES.append(WELCOME_PAGE)


## be sure to use UTF buffer for stdout
sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer)

# Get the cookie. If there's not one, make one.
http_cookie = os.getenv('HTTP_COOKIE')
browser_cookie = False
cookie = ''
if http_cookie:
  for c in http_cookie.split(';'):
    (name, value) = c.split('=', 1)
    if name == 'session' and len(value) == 4 and value.isdigit():
      browser_cookie = True
      cookie = value
      break

if not cookie:
  cookie = str(randint(1000,9999))
  while os.path.exists('sessions/' + cookie):
    cookie = str(randint(1000,9999))

# make the sessions directory if necessary
if not os.path.exists('sessions'):
  os.mkdir('sessions')

# look for any sessions older than 24 hours and delete them
now = time.time()
sessions = glob.glob('sessions/*')
for s in sessions:
  if now - os.path.getmtime(s) > 86400:
    remove_tree(s)

# figure out the path to the current session's directory, creating it
# if necessary
session_path = 'sessions/' + cookie
if cookie and not os.path.exists(session_path):
  os.mkdir(session_path)

print(HTTP_HEADERS % {'cookie':cookie })
form_data = cgi.FieldStorage()
timestamp = datetime.datetime.now().ctime()

if 'sdtf' in form_data:
  ## run autotagger on input

  # step 0, clear old files out of the way
  # and create empty output file
  filelist = glob.glob(session_path+"/output*")
  for f in filelist: os.remove(f)
  open(os.path.join(session_path, 'output.xml'), 'w').close()


  # step 1, get the lines from the form
  infilelines = str(form_data['sdtf'].value, encoding="utf-8").split('\n')

  # step 2 make a TranscriptionFile from the lines
  tf = autotagger.TranscriptionFile(infilelines)
  # check for errors
  if len(tf.errors) > 0:
    errhtml="<pre>"
    for e in tf.errors:
      errhtml+=e
    errhtml+="</pre>"
    print(TEMPATE+WEBPAGES[0] % { 'errors':errhtml })
  else:
   # no errors, run the tagger
    #document = autotagger.setup_DOM()
    #marginheaders, footnotes, xml_ids_dict = autotagger.create_dom_nodes(document, tf)
    #autotagger.organize_nodes(document, tf, marginheaders, footnotes, xml_ids_dict)
    document = autotagger.run(tf)

    #try:
    outfile = open(session_path+"/output.xml", "w",encoding="utf-8")
    #except:
    #  print("error getting the outfile for writing")

    document.writexml(outfile, addindent=" ",newl="\n")
    print(TEMPLATE + WEBPAGES[1] % {'filetype': "TEI-XML", 'timestamp':timestamp,
                          'teioutfile': session_path+"/output.xml",
                          'css':'','htmloutfile':'','texoutfile':''})

elif 'html' in form_data:
  import xslt
  r = xslt.tei2html(session_path+"/output.xml",session_path+"/output.html")
  if r != 0:
    print("<p>xsltproc returned " + str(r) + "</p>")
  else:
    css='#html_span,#html_but { text-decoration:line-through; }\n'
    texout=""
    htmlout="<br />Your HTML is <a href="+session_path+"/output.html>here</a>."
    if(os.path.exists(session_path+"/output.tex")):
      # cross out and disable tex creation as it's already done
      css+='#latex_span,#latex_but { text-decoration:line-through; }'
      texout="<br />Your LaTeX is <a href="+session_path+"/output.tex>here</a>."
    print(TEMPLATE+WEBPAGES[1] % {'filetype': "HTML", 'timestamp':timestamp,
                          'htmloutfile': htmlout, 'css':css, 'texoutfile':texout, 
                          'teioutfile': session_path+"/output.xml" })

elif 'tex' in form_data:
  import xslt
  r = xslt.tei2latex(session_path+"/output.xml",session_path+"/output.tex")
  if r != 0:
    print("<p>xsltproc returned " + str(r) + "</p>")
  else:
    css='#latex_span,#latex_but { text-decoration:line-through; }\n'
    texout="<br />Your LaTeX is <a href="+session_path+"/output.tex>here</a>."
    htmlout=""
    if(os.path.exists(session_path+"/output.html")):
      # cross out and disable html creation as it's already done
      css+='#html_span,#html_but { text-decoration:line-through; }'
      htmlout="<br />Your HTML is <a href="+session_path+"/output.html>here</a>."
    print(TEMPLATE+WEBPAGES[1] % {'filetype': "HTML", 'timestamp':timestamp,
                          'htmloutfile': htmlout, 'css':css, 'texoutfile':texout, 
                          'teioutfile': session_path+"/output.xml" })

else:
  print(TEMPLATE+WEBPAGES[2])
