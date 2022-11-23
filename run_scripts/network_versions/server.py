#!/usr/bin/env python3
import socket
import sys
import time
import ast
import random
import subprocess
import glob
from multiprocessing import Pool
import json
import os
from pymongo import MongoClient

todo = []


def nextAST(s):
    data = ""
    try:
        while True:
            newData = s.recv(1024 * 1024).decode('utf-8')
            if not newData:
                break
            data += newData
            try:
                # print(data)
                ret = ast.literal_eval(data)
                return ret
            except:
                pass
    except:
        return None


def readyNext(mydb):
    ret = None
    while True:
        if (len(todo) == 0):
            break
        next = todo[0]
        cmd = next[0]
        db = next[1]
        print_json_command_to_run = cmd + " --print_JSON " + " 2> /dev/null"
        # print(print_json_command_to_run)
        json_output = subprocess.check_output(print_json_command_to_run, shell=True)
        config = json.loads(json_output)
        collection = mydb["results_" + db]

        if collection.find_one(config):
            todo.remove(todo[0])
        # sys.stderr.write(".")
        # sys.stderr.flush()
        else:
            ret = next
            break

    return ret


def main(port, database):
    # server=arg1.split(":")
    s = socket.socket()
    s.settimeout(1)
    s.bind(("", int(port)))
    s.listen(4096)
    lastCleanup = time.time()
    dispatched = {}
    mongo_client = MongoClient(host=database, serverSelectionTimeoutMS=1000)
    mydb = mongo_client["scheduling_with_simulation"]
    while True:
        try:

            # print("Waiting for collection")
            c, addr = s.accept()
            print('Got connection from', addr)
            rec = nextAST(c)
            if not rec:
                print("	Invalid message")
                c.close()
                continue
            # print(rec)
            # print(rec)
            # rec=ast.literal_eval(rec.decode('utf-8'))
            command = rec["cmd"]

            if (command == "IDLE"):
                print("	" + str(addr) + " Requested Task")

                next = readyNext(mydb)
                if next:
                    print("	Sending task")
                    c.send(str(next[0]).encode('utf-8'))
                    ack = c.recv(1024)
                    print(ack)
                    if (ack == "ACK".encode('utf-8')):
                        print("	Acknowledged")

                        dispatched[next[0]] = {"time": time.time(), "request": todo[0], "db": next[1]}
                        todo.remove(next)
                    else:
                        print("	Not Acknowledged")
                else:
                    print("	Nothing to do")
                    c.send("NONE".encode('utf-8'))
                    ack = c.recv(1024)
            elif (command == "RET"):
                print("	Receiving result")
                data = rec["data"]
                c.send("ACK".encode('utf-8'))
                # add result to database

                collection = mydb["results_" + dispatched[data["runcommand"]]["db"]]
                result = data["result"]
                collection.insert_one(result)
                # print(data)
                dispatched.pop(data["runcommand"])

            elif (command == "ADD"):
                data = rec["data"]
                print(str(addr) + " Adding tasks")
                for d in data:
                    # print("adding "+str(d))
                    todo.append(d)
                print("	Added " + str(len(data)) + " tasks")
                c.send("ACK".encode('utf-8'))
                print("	ingesting...")
                readyNext(mydb)
                print("	ready")
            else:
                print("	unknown command: " + str(rec["cmd"]) + str(rec))
            c.close()

        except socket.timeout:
            pass
        # except Exception as e:
        # print("Error with client ")
        # print(e)
        if lastCleanup - time.time() > 86400:
            for key in dispatched:
                if (dispatched[key]["time"] < lastCleanup):
                    todo.append(dispatched[key]["request"])
                    dispatched.pop(data)
        lastCleanup = time.time()
    mongo_client.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.stderr.write("Usage: " + sys.argv[0] + " <port> <mongo url>\n")
        sys.stderr.write("  For instance: " + sys.argv[0] + " 443 mongodb://localhost:2000\n")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
