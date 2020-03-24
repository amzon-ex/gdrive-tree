# Convert XML to HTML tree
# Bootstrap version
from pathlib import Path
from lxml import etree as xet

filetree = xet.parse(str(Path('out/drive-tree.xml')))
fileroot = filetree.getroot()

lroot = xet.Element('div')
lroot.set('class', 'just-padding')
listtree = xet.ElementTree()
listtree._setroot(lroot)
listroot = xet.SubElement(lroot, 'div')
listroot.set('class','list-group list-group-root well')

def extractNodeLevel(file_current_parent,list_current_parent):			
	for child in file_current_parent:
		listelem = xet.SubElement(list_current_parent, 'a', attrib = {'href' : '#', 'class' : 'list-group-item'})

		if(len(list(child)) > 0):
			listelem.set('href','#item-'+child.attrib['id'])
			listelem.set('data-toggle','collapse')
			xet.SubElement(listelem, 'i', attrib = {'class' : 'fa fa-chevron-right'})
			xet.SubElement(listelem,'span').text = child.attrib['name']
			
			spanelem = xet.SubElement(listelem, 'span', attrib = {'class' : 'badge'})
			spanelem.text = str("{:.2f} KB".format(int(child.attrib['cSize'])/1024.0))
			
			divelem = xet.SubElement(list_current_parent,'div', attrib = {'class' : 'list-group collapse'})
			divelem.set('id','item-'+child.attrib['id'])

			extractNodeLevel(child,divelem)
		else:
			listelem.text = child.attrib['name']

extractNodeLevel(fileroot,listroot)

# SOLVED: Encoding works improperly, Bengali letters remain as escape sequences!
# Apparently works with decode(encoding='utf-8') now, after adding the encoding to `with open(...)`?

# Write the generated tree to an HTML file;
# Setting 'pretty-print' to True automatically adds newlines and indents
with open(Path('out/drive-tree-bs.html'), 'w', encoding = 'utf-8') as f:
	for line in open(Path('res/tree-template-bs.html'), 'rt', encoding = 'utf-8').readlines():
		f.write(line)
		if line.find('<body') > -1:
			f.write('\n' + xet.tostring(listroot, pretty_print = True, encoding = 'utf-8', method = 'html').decode(encoding='utf-8') + '\n')
