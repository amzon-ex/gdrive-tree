
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
# import xml.etree.ElementTree as xet
from lxml import etree as xet

gauth = GoogleAuth()
# Try to load saved client credentials
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there

    # Set access-type to offline to obtain refresh token
    gauth.GetFlow()
    gauth.flow.params.update({'access_type': 'offline'})
    gauth.flow.params.update({'approval_prompt': 'force'})

    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.txt")

drive = GoogleDrive(gauth)


root = xet.Element('root')
tree = xet.ElementTree()
tree._setroot(root)

# Adds a file/folder child to the root of the XML tree including all its sub-children
def addNodeLevel(current_parent,fid = 'root'):
	_f = drive.ListFile({'q': "'{0}' in parents and trashed=false".format(fid)}).GetList()
	sizeSum = 0
	
	# Segregate files and folders into separate lists
	_folders,_files = [],[]
	for f in _f:
		if(f['mimeType'] == 'application/vnd.google-apps.folder'):
			_folders.append(f)
		else:
			_files.append(f)

	# Flush file tags to the tree first
	for file in _files:
		filenode = xet.SubElement(current_parent,'file')
		filenode.set('name',file['title'])
		filenode.set('id',file['id'])
		filenode.set('link',file['alternateLink'])
		filenode.set('type',file['mimeType'])
		try:
			filenode.set('size',file['fileSize'])
		except KeyError:
			filenode.set('size','0')
		sizeSum += int(filenode.attrib['size'])

	# Recursively flush file tags to the tree first
	for folder in _folders:
		print(folder['title']+'...')
		foldernode = xet.SubElement(current_parent,'folder')
		foldernode.set('name',folder['title'])
		foldernode.set('id',folder['id'])
		foldernode.set('link',folder['alternateLink'])

		addNodeLevel(foldernode,folder['id'])

		sizeSum += int(foldernode.attrib['cSize'])
		print('...'+folder['title'])

	current_parent.set('cSize',str(sizeSum))

addNodeLevel(root)
# Write the generated tree to an XML file;
# Setting 'pretty-print' to True automatically adds newlines and indents
# Setting 'xml-declaration' to True writes the XML prolog
tree.write('drive-tree.xml',pretty_print = True,encoding = 'utf-8',xml_declaration = True)