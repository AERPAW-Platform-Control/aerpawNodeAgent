import http.server
import socketserver
from urllib.parse import urlparse
from urllib.parse import parse_qs
import subprocess
import os

def runCmd(cmd):
    shelledResults = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return shelledResults.returncode

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Sending an '200 OK' response
        self.send_response(200)

        # Setting the header
        self.send_header("Content-type", "text/plain")

        # Whenever using 'send_header', you also have to call 'end_headers'
        self.end_headers()

        print("Handling: " + self.path)
        pathPiecesList = self.path.split("/")
        containerStr = pathPiecesList[3]
        print("zeroeth element =" + pathPiecesList[0])

        respond=True
        if self.path.startswith("/v1/fetchContainer/") :
            returned=bytes("OK","utf-8")
            print("Doing a fetchContainer of " + containerStr)
            command = "fetchContainer " + containerStr
            runCmd(command)

        elif self.path.startswith("/v1/startContainer/") :
            returned=bytes("OK","utf-8")
            print ("Doing a startContainer of " + containerStr )
            command = "startContainer " + containerStr
            runCmd(command)

        elif self.path.startswith("/v1/emitDataVolume/") :
            print ("Doing an emitDataVolume of " + containerStr )
            # 1: tar the directory
            # 2: loop, reading a megabyte, writing a MB.
            respond=False  # we're doing the response in here, no need to at the bottom.
            tarCommand = "tar cf /var/local/" + containerStr + ".tar /var/local/" + containerStr
            runCmd(tarCommand)
            # OK, TODO: This is just a quick hack to show tomorrow, need to
            # make this loop and not allocate 20+G of RAM, potentially.
            with open("/var/local/" + containerStr + ".tar", 'r') as file:
                tarFileContents=file.read(-1)
            self.wfile.write(tarFileContents)

        elif self.path.startswith("/v1/deleteDataVolume/") :
            returned=bytes("OK","utf-8")
            print ("Doing a deleteDataVolume of " + containerStr )
            os.remove("/var/local/" + containerStr + ".tar")

        elif self.path.startswith("/v1/killContainer/") :
            returned=bytes("OK","utf-8")
            print ("Doing a killContainer of " + containerStr )
            killCmd="docker kill " + containerStr
            runCmd(killCmd)
            
        else :
            returned=bytes("Unknown REST entrypoint","utf-8")


            # Writing the resulting contents with UTF-8
        self.wfile.write(returned)

        return

# Create an object of the above class
handler_object = MyHttpRequestHandler

PORT = 1887
my_server = socketserver.TCPServer(("", PORT), handler_object)

# Star the server
my_server.serve_forever()

