# Convert XML to HTML tree
# Bare HTML version, lightweight
from pathlib import Path
from lxml import etree as xet

listroot = xet.Element('ul')
listroot.set('id','myUL')
listtree = xet.ElementTree()
listtree._setroot(listroot)

filetree = xet.parse(str(Path('out/drive-tree.xml')))
fileroot = filetree.getroot()

def extractNodeLevel(file_current_parent,list_current_parent):
	isrootnode = False
	if 'id' in list_current_parent.attrib:
		if(list_current_parent.attrib['id'] == 'myUL'):
			isrootnode = True
	if(not isrootnode):
		list_current_parent = xet.SubElement(list_current_parent,'ul')
		list_current_parent.set('class','nested');
			
	for child in file_current_parent:
		listelem = xet.SubElement(list_current_parent,'li')
		if(len(list(child)) > 0):
			spanelem = xet.SubElement(listelem,'span')
			spanelem.set('class','caret')
			spanelem.text = child.attrib['name']
			extractNodeLevel(child,listelem)
		else:
			listelem.text = child.attrib['name']

extractNodeLevel(fileroot,listroot)

# SOLVED: Encoding works improperly, Bengali letters remain as escape sequences!
# Apparently works with decode(encoding='utf-8') now, after adding the encoding to `with open(...)`?

# Write the generated tree to an HTML file;
# Setting 'pretty-print' to True automatically adds newlines and indents
with open(Path('out/drive-tree-html.html'), 'w+', encoding = 'utf-8') as f:
    for line in open(Path('res/tree-template.html'), 'rt', encoding = 'utf-8').readlines():
        f.write(line)
        if line.find('<body>') > -1:
            f.write('\n' + xet.tostring(listroot, pretty_print = True, encoding = 'utf-8', method = 'html').decode(encoding='utf-8') + '\n')
