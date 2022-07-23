# Python-Code-to-load-Data-from-Web and Store in SharePoint
While executing the Python code, if we are not able to install any Python Package due to "Certificate issue" like: [SSL: CERTIFICATE_VERIFY_FAILED]

**Then Add below highlighted part while installing any Python Package:-**

**Code:** "pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org selenium"

**Create Executable(.exe) File of Python Script:** Install "PyInstaller" Package.

**Code:** "pyinstaller --onefile pythonScriptName.py"
