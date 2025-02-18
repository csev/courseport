from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from bs4 import BeautifulSoup
import xml.dom.minidom as minidom
import re
import zipfile
import base64
import html
import tarfile

# Create your views here.


class UploadView(View) :
    def get(self, request):
        return render(request, 'upload/index.html')

    def post(self, request):
        uploaded_file = request.FILES['zip']
        try:
            pieces = process_archive_file(uploaded_file)
            context = { 'title': uploaded_file, 'pieces': pieces }
            return render(request, 'upload/zipdump.html', context)
        except Exception as e:
            return render(request, 'upload/error.html', {'error': str(e)})

def process_archive_file(archive_file):
    pieces = list()
    idvalue = 0
    
    # Determine file type and open appropriate handler
    if hasattr(archive_file, 'name'):
        filename = archive_file.name.lower()
        if filename.endswith('.tar.gz') or filename.endswith('.tgz'):
            # For tar.gz files, we need to save to disk temporarily
            with open('/tmp/temp_archive', 'wb') as tmp:
                for chunk in archive_file.chunks():
                    tmp.write(chunk)
            archive = tarfile.open('/tmp/temp_archive', 'r:gz')
            file_list = archive.getnames()
        else:  # Assume ZIP
            archive = zipfile.ZipFile(archive_file)
            file_list = archive.namelist()
    
    for fname in file_list:
        idvalue += 1
        piece = dict()
        piece['idvalue'] = idvalue
        piece['fname'] = fname

        # Handle directories
        if isinstance(archive, zipfile.ZipFile):
            isdir = zipfile.Path(root=archive, at=fname).is_dir()
        else:  # tarfile
            isdir = archive.getmember(fname).isdir()
            
        if isdir:
            piece['folder'] = isdir
            pieces.append(piece)
            continue

        # Read file data
        if isinstance(archive, zipfile.ZipFile):
            with archive.open(fname) as hand:
                data = hand.read()
        else:  # tarfile
            member = archive.getmember(fname)
            data = archive.extractfile(member).read() if archive.extractfile(member) else b''
        
        piece['size'] = len(data)
        
        # Process based on file extension
        if fname.endswith('.jpg'):
            piece['type'] = 'jpg'
            data_base64 = base64.b64encode(data).decode()
            htm = '<img src="data:image/jpeg;base64,' + data_base64 + '"><br/>'
            piece['html'] = htm
        elif fname.endswith('.png'):
            piece['type'] = 'png'
            data_base64 = base64.b64encode(data).decode()
            htm = '<img src="data:image/png;base64,' + data_base64 + '"><br/>'
            piece['html'] = htm
        elif fname.endswith('.txt'):
            piece['type'] = 'txt'
            htm = "<pre>\n" + html.escape(data.decode()) + "\n</pre>\n"
            piece['html'] = htm
        elif fname.endswith('.xml'):
            piece['type'] = 'xml'
            xmlstr = data.decode()
            try:
                dom = minidom.parseString(data)
                note = ""
            except Exception as e:
                soup = BeautifulSoup(xmlstr, "xml")
                dom = minidom.parseString(soup.prettify())
                note = "XML parse failed "+str(e)+"\n"+"Re-parsed with BeautifulSoup\n"
            for elem in dom.getElementsByTagName("property"):
                if elem.nodeName == "property":
                    if elem.getAttribute("enc") != "BASE64": continue
                    decoded = base64.b64decode(elem.getAttribute("value"))
                    elem.setAttribute("B64Decoded", decoded.decode())
            xmlstr = dom.toprettyxml(encoding="utf-8")
            xmlstr = note + xmlstr.decode()
            xmlstr = re.sub(r'^\s*\n', '', xmlstr, flags=re.MULTILINE)
            htm = "<pre>\n" + html.escape(xmlstr) + "\n</pre>\n"
            piece['html'] = htm
        elif fname.endswith('.html'):
            piece['type'] = 'html'
            piece['html'] = data.decode()

        pieces.append(piece)
    
    # Clean up if we created a temporary file
    if isinstance(archive, tarfile.TarFile):
        import os
        os.remove('/tmp/temp_archive')
        
    return pieces
