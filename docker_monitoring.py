import os
import json
import sys
import subprocess


def main():
    if (len(sys.argv)) != 3:
        print("Usage: docker_monitoring.py <config.json path> <data.json path>")
        sys.exit(1)

    call_docker_info = subprocess.run(['docker info'], shell=True,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
    if call_docker_info.returncode == 1:
        print("Docker isn't running!")
        sys.exit(1)

    configFile = open(sys.argv[1], 'r+')
    configFileSize = os.stat(sys.argv[1]).st_size
    if (configFileSize == 0):
        configFile.write("{}")
    dataFile = open(sys.argv[2], 'r+')
    dataFileSize = os.stat(sys.argv[2]).st_size
    if (dataFileSize == 0):
        dataFile.write("{}")

    config = json.load(configFile)
    data = {}

    for containerKey in config["containers"]:
        containerConfig = config["containers"][containerKey]

        status = subprocess.run(['docker inspect'
                                + ' -f \'{{.State.Status}}\' '
                                + containerKey],
                                shell=True, stdout=subprocess.PIPE)
        if status.stdout.decode('utf-8').strip() == "exited":
            data[containerKey] = {"status": "exited"}
            if containerConfig.get("stopped"):
                subprocess.run([containerConfig["stopped"]], shell=True)
            continue
        status_restarting = subprocess.run(['docker inspect'
                                            + ' -f \'{{.State.Restarting}}\' '
                                            + containerKey],
                                           shell=True, stdout=subprocess.PIPE)
        if status_restarting.stdout.decode('utf-8').strip() == "true":
            data[containerKey] = {"status": "restarting"}
            if containerConfig.get("restarting"):
                subprocess.run([containerConfig["restarting"]], shell=True)
            continue
        else:
            data[containerKey] = {"status": "running"}

    configFile.close()
    json.dump(data, dataFile)
    dataFile.close()


if __name__ == '__main__':
    main()
