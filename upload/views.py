from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from bs4 import BeautifulSoup
import xml.dom.minidom as minidom
import re
import zipfile
import base64
import html

# Create your views here.


class UploadView(View) :
    def get(self, request):
        return render(request, 'upload/index.html')

    def post(self, request):
        zf = request.FILES['zip']
        try:
            pieces = process_zip_file(zf)
            context = { 'title': zf, 'pieces': pieces }
            return render(request, 'upload/zipdump.html', context)
        except Exception as e:
            return render(request, 'upload/error.html', {'error': str(e)})

def process_zip_file(zip_file):
    zfile = zipfile.ZipFile(zip_file)
    idvalue = 0
    pieces = list()
    for fname in zfile.namelist():
        idvalue = idvalue + 1
        piece = dict()
        piece['idvalue'] = idvalue
        piece['fname'] = fname

        isdir = zipfile.Path(root=zfile, at=fname).is_dir()
        if isdir : 
            piece['folder'] = isdir
            pieces.append(piece)
            continue
        with zfile.open(fname) as hand:
            data = hand.read()
            piece['size'] = len(data)
            if fname.endswith('.jpg') : 
                piece['type'] = 'jpg'
                data_base64 = base64.b64encode(data).decode()
                htm = '<img src="data:image/jpeg;base64,' + data_base64 + '"><br/>'
                piece['html'] = htm
            elif fname.endswith('.png') : 
                piece['type'] = 'png'
                data_base64 = base64.b64encode(data).decode()
                htm = '<img src="data:image/png;base64,' + data_base64 + '"><br/>'
                piece['html'] = htm
            elif fname.endswith('.txt') :
                piece['type'] = 'txt'
                htm = "<pre>\n" + html.escape(data.decode()) + "\n</pre>\n"
                piece['html'] = htm
            elif fname.endswith('.xml') :
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
                    if elem.nodeName == "property" :
                        if elem.getAttribute("enc") != "BASE64" : continue
                        decoded = base64.b64decode(elem.getAttribute("value"))
                        elem.setAttribute("B64Decoded", decoded.decode())
                xmlstr = dom.toprettyxml(encoding="utf-8")
                xmlstr = note + xmlstr.decode()
                xmlstr = re.sub(r'^\s*\n', '', xmlstr, flags=re.MULTILINE)
                htm = "<pre>\n" + html.escape(xmlstr) + "\n</pre>\n"
                piece['html'] = htm
            elif fname.endswith('.html') :
                piece['type'] = 'html'
                piece['html'] = data.decode()

        pieces.append(piece)
    return pieces
