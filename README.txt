This is a multi-client chatting application developed by Yuechuan Zhang (Robert) and Haojia He (Owen).

To run the application, you can either:
1. run the executable file (instruction provided in HOWTO.txt)

2. run the source code (this allows you to do custom set up in the config.py file)
    a. start terminal, cd /source_code and do "pip install -r requirements.txt"
    b. open config.py and set up your own configuration including
            - port number
            - RSA public/private key pair
            - server secret
            - other parameter related  to the infrastructure (don't touch it unless you know you what you are doing)
    c. do "python app.py" to start the server
    d. visit 127.0.0.1:{your configed port number}/login


