# gdrive-tree

Extract and store file/folder size information from a Google Drive account in a tree format.

To use this app, you first need to obtain OAuth 2.0 client ID from the [Google API Console][apiconsole].
Instructions for the same can be found [here][oauth2].

Rename the obtained json file to `client_secrets.json` and you're good to go. The first time you run the script, an authorization procedure will be initiated and an access token will be obtained and saved to `mycreds.txt`.

Then it's as simple as running `python buildtree.py`.

For a quick and dirty visualization of the XML file, use `python x2html.py`. An output HTML will be generated in the `out` folder.

For a prettier visualization, use `python x2html-tree-alt.py`. Since this one uses javascript, the page might not function as expected unless you start a local server. This is also as easy as doing `python -m http.server` in the `out` folder.


### Requirements:
 - pydrive
 - lxml

[apiconsole]: <https://console.developers.google.com/>
[oauth2]: <https://developers.google.com/identity/protocols/oauth2>