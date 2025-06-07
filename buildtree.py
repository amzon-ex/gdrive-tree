from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pathlib import Path
from lxml import etree as xet
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
from datetime import timedelta

def format_time(seconds):
    """Format seconds into a human-readable string"""
    return str(timedelta(seconds=int(seconds)))

gauth = GoogleAuth()
# Set the scopes we need
gauth.settings['oauth_scope'] = [
    'https://www.googleapis.com/auth/drive.readonly'  # Read-only access to files and metadata
]

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

# Create a thread pool for synchronous PyDrive operations
thread_pool = ThreadPoolExecutor(max_workers=20)

async def list_files_async(fid):
    """Run PyDrive's ListFile in a thread pool"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        thread_pool,
        lambda: drive.ListFile({'q': f"'{fid}' in parents and trashed=false"}).GetList()
    )

async def addNodeLevel(current_parent, fid='root'):
    """Asynchronously add nodes to the tree"""
    _f = await list_files_async(fid)
    sizeSum = 0
    
    # Segregate files and folders into separate lists
    _folders, _files = [], []
    for f in _f:
        if f['mimeType'] == 'application/vnd.google-apps.folder':
            _folders.append(f)
        else:
            _files.append(f)

    # Process files
    for file in _files:
        # Skip Google Drive shortcuts
        if file['mimeType'] == 'application/vnd.google-apps.shortcut':
            continue
            
        filenode = xet.SubElement(current_parent, 'file')
        filenode.set('name', file['title'])
        filenode.set('id', file['id'])
        filenode.set('link', file['alternateLink'])
        filenode.set('type', file['mimeType'])
        if 'fileSize' in file:
            filenode.set('size', file['fileSize'])
        elif 'quotaBytesUsed' in file:
            filenode.set('size', file['quotaBytesUsed'])
        else:
            filenode.set('size', '0')
        sizeSum += int(filenode.attrib['size'])

    # Process folders concurrently
    folder_tasks = []
    for folder in _folders:
        # print(folder['title'] + '...')
        foldernode = xet.SubElement(current_parent, 'folder')
        foldernode.set('name', folder['title'])
        foldernode.set('id', folder['id'])
        foldernode.set('link', folder['alternateLink'])
        
        # Create task for each folder
        task = asyncio.create_task(addNodeLevel(foldernode, folder['id']))
        folder_tasks.append((foldernode, task))

    # Wait for all folder tasks to complete
    for foldernode, task in folder_tasks:
        await task
        sizeSum += int(foldernode.attrib['cSize'])
        print('...' + foldernode.attrib['name'])

    current_parent.set('cSize', str(sizeSum))

async def main():
    start_time = time.time()
    print(f"Starting tree generation at {time.strftime('%H:%M:%S')}")
    
    root = xet.Element('root')
    root.set('id', 'gdrive-tree-root')
    tree = xet.ElementTree()
    tree._setroot(root)

    await addNodeLevel(root)
    
    # Write the generated tree to an XML file
    tree.write(str(Path('out/drive-tree.xml')), pretty_print=True, encoding='utf-8', xml_declaration=True)
    
    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nTree generation completed at {time.strftime('%H:%M:%S')}")
    print(f"Total runtime: {format_time(total_time)}")

if __name__ == "__main__":
    asyncio.run(main())