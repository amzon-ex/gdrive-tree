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

def isGoogleDoc(mimeType):
    return mimeType.startswith('application/vnd.google-apps.')

def getGoogleDocIcon(mimeType):
    if 'document' in mimeType:
        return 'fa-solid fa-file-word'  # Word document icon
    elif 'spreadsheet' in mimeType:
        return 'fa-solid fa-file-excel'  # Excel spreadsheet icon
    elif 'presentation' in mimeType:
        return 'fa-solid fa-file-powerpoint'  # PowerPoint icon
    elif 'form' in mimeType:
        return 'fa-solid fa-file-lines'  # Form icon
    elif 'drawing' in mimeType:
        return 'fa-solid fa-paintbrush'  # Drawing icon
    else:
        return 'fa-solid fa-file-lines'  # Generic document icon

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

    return cSize, sizePrefix, int(sizeString)  # Return raw size for sorting

def getSizeColor(size):
    # Define size thresholds and corresponding colors
    if size < 1024 * 1024:  # Less than 1MB
        return '#00cc00'  # Darker Green
    elif size < 10 * 1024 * 1024:  # Less than 10MB
        return '#ff9900'  # Orange
    elif size < 100 * 1024 * 1024:  # Less than 100MB
        return '#ff6600'  # Dark Orange
    else:
        return '#ff0000'  # Red

def extractNodeLevel(file_current_parent,list_current_parent):
    global is_gdrive_tree_root

    divelem = xet.SubElement(list_current_parent, 'div')

    # The name element
    nameelem = xet.SubElement(divelem, 'span', attrib = {'class' : 'name'})
    xet.SubElement(nameelem, 'i', attrib = {'class' : 'fa-solid fa-folder-open'})
    if (is_gdrive_tree_root):
        xet.SubElement(nameelem, 'span').text = ' gdrive-tree-root'
    else:
        xet.SubElement(nameelem, 'span').text = ' ' + file_current_parent.attrib['name']

    # The size element
    sizeelem = xet.SubElement(divelem, 'span', attrib = {'class' : 'size'})
    cSize, sizePrefix, rawSize = sizePretty(file_current_parent.attrib['cSize'])
    sizeelem.text = str(f"{cSize:.2f} {sizePrefix}B")
    sizeelem.set('style', f'color: {getSizeColor(rawSize)}')

    is_gdrive_tree_root = False

    list_current_parent = xet.SubElement(list_current_parent, 'ul', attrib = {'class' : 'nested'})

    # Sort children by size
    children = list(file_current_parent)
    children.sort(key=lambda x: int(x.attrib.get('cSize', x.attrib.get('size', '0'))), reverse=True)

    for child in children:
        listelem = xet.SubElement(list_current_parent,'li')

        if(len(list(child)) > 0):
            extractNodeLevel(child, listelem)
        else:
            divelem = xet.SubElement(listelem, 'div')

            # The name element
            nameelem = xet.SubElement(divelem, 'span', attrib = {'class' : 'name'})
            
            # Check if it's a Google Doc
            if 'type' in child.attrib and isGoogleDoc(child.attrib['type']):
                # Use appropriate Google Doc icon
                xet.SubElement(nameelem, 'i', attrib = {'class' : getGoogleDocIcon(child.attrib['type'])})
                # Add a special class for Google Docs
                nameelem.set('class', 'name google-doc')
            else:
                xet.SubElement(nameelem, 'i', attrib = {'class' : 'fa-solid fa-file'})
            
            xet.SubElement(nameelem, 'span').text = ' ' + child.attrib['name']

            # Add size for files too, but not for Google Docs
            if 'size' in child.attrib:
                sizeelem = xet.SubElement(divelem, 'span', attrib = {'class' : 'size'})
                cSize, sizePrefix, rawSize = sizePretty(child.attrib['size'])
                sizeelem.text = str(f"{cSize:.2f} {sizePrefix}B")
                sizeelem.set('style', f'color: {getSizeColor(rawSize)}')

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
