#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import os
import json
import subprocess

secret_data = {}

def read_secrets_config():
    global secret_data
    secret_data["images"] = {}

    registry_url_path = "/mnt/registry/url"
    if not os.path.isfile(registry_url_path):
        throw("/mnt/registry/url doesn't exist")

    registry_file = open(registry_url_path, "r")
    secret_data["registry_url"] = registry_file.read()

    images_root_path = "/mnt/images"
    image_names = [d for d in os.listdir(images_root_path) if os.path.isdir(os.path.join(images_root_path, d))]

    for image_name in image_names:
        deployment_filepath = os.path.join(images_root_path,image_name,"deployment")
        container_filepath = os.path.join(images_root_path,image_name,"container")
        if os.path.isfile(deployment_filepath) and os.path.isfile(container_filepath):
            f1 = open(deployment_filepath, "r")
            deployment_name = f1.read()
            f2 = open(container_filepath, "r")
            container_name = f2.read()

            secret_data["images"][image_name] = {}
            secret_data["images"][image_name]["deployment"] = deployment_name
            secret_data["images"][image_name]["container"] = container_name

def check_and_update_deployment_image(decoded_post_data):
    obj = json.loads(decoded_post_data)
    event_obj = obj["events"][0]
    if event_obj["action"] == "push":
        if event_obj["target"]["mediaType"] == "application/vnd.docker.distribution.manifest.v2+json":
            logging.info("Received new image notification")
            new_image_name = event_obj["target"]["repository"]
            base_image_name = new_image_name.split("_")[0]

            # Deployment infos
            deployment_name = secret_data["images"][base_image_name]["deployment"]
            container_name = secret_data["images"][base_image_name]["container"]
            registry_url = secret_data["registry_url"]
            # Update cluster deployment image
            run_command_arr = ["kubectl", "set", "image", "deployment/" + deployment_name, container_name + "=" + registry_url + "/" + new_image_name]
            logging.info("Updating deployment : " + deployment_name + " to image " + new_image_name)
            logging.info(run_command_arr)
            subprocess.run(run_command_arr)


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        decoded_post_data = post_data.decode('utf-8')
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), decoded_post_data)

        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=S, port=80):
    logging.basicConfig(filename="httpd.log",level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    read_secrets_config()
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()

