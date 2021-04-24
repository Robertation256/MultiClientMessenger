This is a multi-client chatting application designed by Yuechuan Zhang (Robert) and Haojia He (Owen).

To run the application, read through the provided HOWTO.txt file for requirements installation.

List of files:

MultiClientMessenger % ls -R
HOWTO.txt		common			static
README.md		config.py		templates
__pycache__		dto			utils
app.py			requirements.txt

./__pycache__:
config.cpython-37.pyc	config.cpython-38.pyc

./common:
ChatServer.py	__pycache__	handlers	templates

./common/__pycache__:
ChatServer.cpython-37.pyc	ChatServer.cpython-38.pyc

./common/handlers:
LoggedInUserHandler.py		__pycache__
PublicConnectionHandler.py

./common/handlers/__pycache__:
LoggedInUserHandler.cpython-37.pyc	PublicConnectionHandler.cpython-38.pyc
LongConnectionHandler.cpython-37.pyc	ShortConnectionHandler.cpython-37.pyc
PublicConnectionHandler.cpython-37.pyc	ShortConnectionHandler.cpython-38.pyc

./common/templates:
Request.py	Response.py	__pycache__

./common/templates/__pycache__:
Request.cpython-37.pyc	Response.cpython-37.pyc
Request.cpython-38.pyc	Response.cpython-38.pyc

./dto:
User.py		__pycache__

./dto/__pycache__:
User.cpython-37.pyc

./static:
css	image	js

./static/css:
chatroom.css	login.css

./static/image:
avatar01.jpg		avatar07.jpg		avatar13.jpg
avatar02.jpg		avatar08.jpg		avatar14.jpg
avatar03.jpg		avatar09.jpg		avatar15.jpg
avatar04.jpg		avatar10.jpg		favicon.ico
avatar05.jpg		avatar11.jpg		favicon.jpg
avatar06.jpg		avatar12.jpg		refreshbutton.jpg

./static/js:
chatroom.js	login.js

./templates:
chatroom.html	login.html

./utils:
DESCrypto.py	RSACrypto.py	__pycache__

./utils/__pycache__:
DESCrypto.cpython-37.pyc	RSACrypto.cpython-37.pyc
DESCrypto.cpython-38.pyc