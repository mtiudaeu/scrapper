#!/usr/bin/env python

#FIXME Add clean up of registry

import sys, tempfile, os, shutil, subprocess, json, logging, time

git_url = ""
registry_url = ""
git_tag = ""
docker_dir = "docker-images"

def does_images_exist_on_registry(image_name):
    logging.info("Check if exist " + image_name)

    p1 = subprocess.Popen(["git", "tag"], stdout=subprocess.PIPE)
    p1 = subprocess.Popen(["curl", "--insecure", "-X", "GET", "https://localhost:443/v2/_catalog"], stdout=subprocess.PIPE)
    json_str = str(p1.communicate()[0]).strip("b'\\n")
    json_obj = json.loads(json_str)
    repository_images = json_obj["repositories"]
    for i in range(0,len(repository_images)):
        if repository_images[i] == image_name:
            return True

    return False

def clean_up_registry():

    logging.info("Clean up registry")

    p1 = subprocess.Popen(["curl", "--insecure", "-X", "GET", "https://localhost:443/v2/_catalog"], stdout=subprocess.PIPE)
    json_str = str(p1.communicate()[0]).strip("b'\\n")
    json_obj = json.loads(json_str)
    repository_images = json_obj["repositories"]
    for i in range(0,len(repository_images)):
        if git_tag not in repository_images[i]:
            shutil.rmtree("/mnt/registry/docker/registry/v2/repositories/" + repository_images[i])

def clone_git_and_update_images():
    logging.info("call clone_git_and_update_images")

    tmp_dirpath = tempfile.mkdtemp()
    os.chdir(tmp_dirpath)

    logging.info("git clone")
    subprocess.run(["git", "clone", git_url])
    splited_str = git_url.replace(".git","").split("/")

    os.chdir(splited_str[len(splited_str)-1])

    logging.info("git tag")
    p1 = subprocess.Popen(["git", "tag"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["tail", "-1"], stdin=p1.stdout, stdout=subprocess.PIPE)
    git_tag = str(p2.communicate()[0]).strip("b'\\n")

    subprocess.run(["git", "checkout", "tags/" + git_tag, "-b", "latest_tag"])

    os.chdir(docker_dir)
    dir_list = os.listdir()

    for i in range(0,len(dir_list)):
        docker_image_name = dir_list[i]
        os.chdir(docker_image_name)
        docker_image_name = docker_image_name + "_" + git_tag

        if not does_images_exist_on_registry(docker_image_name):
            logging.info("Build image " + docker_image_name)
            remote_image_name = registry_url + "/" + docker_image_name
            subprocess.run(["docker", "build", "-t", remote_image_name, "."])
            subprocess.run(["docker", "push", remote_image_name])
            subprocess.run(["docker", "rmi", remote_image_name])

        else:
            logging.info(docker_image_name + " already exist")

        os.chdir("..")

    shutil.rmtree(tmp_dirpath)

    clean_up_registry()

#main
logging.basicConfig(filename="update-registry.log", level=logging.INFO, format='%(asctime)s %(message)s')

args_len = len(sys.argv)
if args_len != 3:
    logging.info("Invalid number of argument. Exiting")
    raise "update-registry.py <git-url> <registry-url>"

git_url = sys.argv[1]
registry_url = sys.argv[2]

while 1 :
    clone_git_and_update_images()
    time.sleep(120) # sleep 2 min


