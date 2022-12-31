# Convert XML to an interactive tree
# More expensive HTML version
from pathlib import Path
from lxml import etree as xet

listroot = xet.Element('div', attrib = {'class' : 'tree'})
listtree = xet.ElementTree()
listtree._setroot(listroot)

driveroot = xet.SubElement(xet.SubElement(listroot, 'ul'), 'li')
is_gdrive_tree_root = True

filetree = xet.parse(str(Path('out/drive-tree.xml')))
fileroot = filetree.getroot()

def sizePretty(sizeString):
    sizeDigits = len(sizeString)
    cSize = int(sizeString)
    sizeFactor = 0
    sizePrefix = ''
    if (sizeDigits > 3 and sizeDigits <= 6):
        sizeFactor = 1
        sizePrefix = 'K'
    elif (sizeDigits > 6 and sizeDigits <= 9):
        sizeFactor = 2
        sizePrefix = 'M'
    elif (sizeDigits > 9):
        sizeFactor = 3
        sizePrefix = 'G'
    cSize /= 1024.0**sizeFactor

    return cSize, sizePrefix

def extractNodeLevel(file_current_parent,list_current_parent):
    global is_gdrive_tree_root

    divelem = xet.SubElement(list_current_parent, 'div')

    # The name element
    nameelem = xet.SubElement(divelem, 'span', attrib = {'class' : 'name'})
    xet.SubElement(nameelem, 'i', attrib = {'class' : 'fa fa-folder-open'})
    # nameelem.text = child.attrib['name']
    if (is_gdrive_tree_root):
        xet.SubElement(nameelem, 'span').text = ' gdrive-tree-root'
    else:
        xet.SubElement(nameelem, 'span').text = ' ' + file_current_parent.attrib['name']

    # The size element
    sizeelem = xet.SubElement(divelem, 'span', attrib = {'class' : 'size'})
    cSize, sizePrefix = sizePretty(file_current_parent.attrib['cSize'])
    sizeelem.text = str(f"{cSize:.2f} {sizePrefix}B")

    is_gdrive_tree_root = False

    list_current_parent = xet.SubElement(list_current_parent, 'ul', attrib = {'class' : 'nested'})

    for child in file_current_parent:
        listelem = xet.SubElement(list_current_parent,'li')

        if(len(list(child)) > 0):
            extractNodeLevel(child, listelem)

        else:
            divelem = xet.SubElement(listelem, 'div')

            # The name element
            nameelem = xet.SubElement(divelem, 'span', attrib = {'class' : 'name'})
            xet.SubElement(nameelem, 'i', attrib = {'class' : 'fa fa-file'})
            # nameelem.text = child.attrib['name']
            xet.SubElement(nameelem, 'span').text = ' ' + child.attrib['name']

extractNodeLevel(fileroot,driveroot)

# SOLVED: Encoding works improperly, Bengali letters remain as escape sequences!
# Apparently works with decode(encoding='utf-8') now, after adding the encoding to `with open(...)`?

# Write the generated tree to an HTML file;
# Setting 'pretty-print' to True automatically adds newlines and indents
with open(Path('out/drive-tree-alt.html'), 'w+', encoding = 'utf-8') as f:
    for line in open(Path('res/tree-template-2.html'), 'rt', encoding = 'utf-8').readlines():
        f.write(line)
        if line.find('<div id="collapseDVR3" class="panel-collapse collapse in">') > -1:
            f.write('\n' + xet.tostring(listroot, pretty_print = True, encoding = 'utf-8', method = 'html').decode(encoding='utf-8') + '\n')
