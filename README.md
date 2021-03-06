# Post'Em Tool for Canvas

Post 'Em is a tool that allows you to upload and post a spreadsheet with special access controls for your students. It is used by many as an alternative to Sakai's Gradebook tool. You can create a spreadsheet with a row for each student and a column for each entry. The benefit of Post 'Em is that you are free to enter in any data you wish, as opposed to the numeric grade-based Gradebook tool. It allows you to enter traditional numeric grade scores, but accompanied with more in-depth feedback and comments.

My former colleague, Becky Kinney, brought this tool from Sakai to Canvas. However, the tool is broken due to the changes in Canvas API. Initially, this tool is written in PHP. To learn Python and Flask, I decided to "reinvent the wheel", and rename it to "Post'Em Plus". This tool can be quickly deployed to Heroku for testing. It uses AWS S3 to store CSV files, which enables versioning and extra security features. Moreover, the user interface is aligned with Canvas styles now. The tool can also be deployed to your local server. You may find tons of tutorials regarding how to deploy Flask app. Finally, I'm very new to the Python's world, and this is my first time using Flask for developing a web app. If you find any bugs or places can be improved, please do let me know. Should you have any questions and concerns, feel free to create a "new issue". I will try my best to answer it.

## Getting Started

### Prerequisites

* Canvas API token with admin access.
* AWS S3 access key & secret (It is recommended to enable "Versioning" on AWS S3)

```
git clone https://github.com/jasonhemu/postem_plus_open.git
```

### Edit settings.py

Make sure to replace all the required areas.

### Deploy to Heroku

Click on this button -> [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

### Edit static/lti.xml

You may use this tool (https://www.edu-apps.org/build_xml.html) to regenerate your XML file.

### Install the tool on your Canvas instance

* Have the XML, consumer key, and secret ready.
* Navigate to the course that you would like the LTI to be added to. Click Settings in the course navigation bar. Then, select the Apps tab. Near the tabs on the right side, click 'View App Configurations'. It should lead to a page that lists what LTIs are inside the course. Click the button near the tabs that reads '+ App'.
* A modal should come up that allows you to customize how the app gets added. Change the configuration in the Configuration Type dropdown menu to 'By URL' or 'Paste XML' depending on how you have your LTI configured. If your LTI is publicly accessible, 'By URL' is recommended. From there, fill out the Name and Consumer Keys, and the Config URL or XML Configuration. Click Submit.
* Your LTI will appear depending on specifications in the XML.

## Built With

* [Flask](https://github.com/pallets/flask)
* [PyLTI](https://github.com/mitodl/pylti)
* [Bootstrap](https://getbootstrap.com/docs/4.0/getting-started/introduction/)
* [jQuery Popup Overlay](https://github.com/vast-engineering/jquery-popup-overlay)
* [Dropzone.js](http://www.dropzonejs.com/)

## Inspired By

* My former colleague [Becky Kinney](http://sites.udel.edu/bkinney/2013/12/04/postem-for-canva-updates/)
* [UCF Open](https://github.com/ucfopen/lti-template-flask)

## License

![Creative Commons License](https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png)

This work is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-nc-sa/4.0/)

## Author

* Mu He - Educational Technology Consultant at [University of Delaware](http://sites.udel.edu/ats/)
