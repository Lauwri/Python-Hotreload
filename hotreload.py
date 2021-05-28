#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import re
import stat
import time
import argparse 
import subprocess

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

###
## Arguments
###
text="Python hotreload"
parser = argparse.ArgumentParser(description=text)
parser.add_argument('path', metavar='P', type=str, help='Reload path')
parser.add_argument('arguments', metavar='A', nargs='*', type=str, help='Arguments for reloadable')
parser.add_argument("-e", "--env-var", nargs='*', type=str, help="Environment variables key=value")
parser.add_argument("-I", "--Include", nargs='*', type=str, help="Include directory to watch, default='./'")
parser.add_argument("-pv", "--python-version", type=float, help="use python version, default=3")
parser.add_argument("-V", "--Version", help="show application version", action="store_true")
parser.add_argument("-s", "--silent", help="Minimize logging", action="store_true")
parser.add_argument("-ss", "--super-silent", help="No logs", action="store_true")
args = parser.parse_args()

###
## Utilities
###
class styles:
  HEADER = '\033[95m'
  BLUE = '\033[94m'
  CYAN = '\033[96m'
  GREEN = '\033[92m'
  WARNING = '\033[93m'
  CRITICAL = '\033[91m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'
  ENDC = '\033[0m'

def prettyPrint(msg, style=styles.GREEN, loud=False):
  if args.super_silent or args.silent and not loud:
    return
  print(style + msg + styles.ENDC)

def parseEnv(rawEnv):
  if rawEnv:
    return dict(env.split("=") for env in rawEnv)

def parsePath(rawPath):
  return os.path.abspath(rawPath)

def isUnder(dir, dirs):
  is_under = False
  for path in dirs:
    if path == dir:
      break
    if os.path.abspath(path)+"/" in os.path.abspath(dir)+"/":
      is_under = True
  return is_under

def chmodPrompt(path):
  prettyPrint("Trying to give +x permission to file:\n%s " % path, styles.WARNING)
  if input("Are you sure? (y/n)") != "y":
    return
  os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
  

class Reload(FileSystemEventHandler):
  process = None
  python = None
  path = None
  arguments = None
  env_vars = None
  def __init__(self, path, arguments, env_vars, version=3):
    self.python = "python%s"%version
    self.path = path
    self.arguments = arguments
    self.env_vars = env_vars
    self.reload()
    super(Reload, self).__init__()

  #System listeners TODO: add listen levels in arguments
  def on_moved(self, event):
    self.reload()
  def on_created(self, event):
    self.reload()
  def on_deleted(self, event):
    self.reload()
  def on_modified(self, event):
    self.reload()

  #TODO: Process stdin, stdout and stderr pipe
  def reload(self):
    msg = "Loading"
    if(self.process):
      self.kill()
      msg = "Reloading"
    prettyPrint(msg+" script with command: %s" % " ".join([self.python, re.split(r'/|\\', self.path)[-1], self.arguments]) , styles.WARNING, True)
    try:
      self.process = subprocess.Popen([self.python, self.path, self.arguments], env=self.env_vars)
    except PermissionError:
      prettyPrint("Failed to execute file with permission error", styles.CRITICAL, True)
      chmodPrompt(self.path)

  def kill(self):
    self.process.kill()

###
## Variables
###
if args.Version:
  prettyPrint("Python hotreloader 1.0", styles.BOLD, True)
  sys.exit(1)

path = parsePath(args.path)
arguments = ' '.join(args.arguments)
env_var = parseEnv(args.env_var)
paths = ['./']
version = 3
if args.Include:
  paths = args.Include
if args.python_version:
  version = args.python_version

###
## Info
###
prettyPrint("*** Python hotreloader 1.0 ***", styles.HEADER)
prettyPrint("Reload full path: %s" % path, styles.CYAN)
prettyPrint("With arguments: %s" % arguments)
prettyPrint("With environment variables: %s" % env_var)
prettyPrint("Watching paths: %s" % paths)
prettyPrint("Running python version: %s" % version)

###
## Hotreload
###
hot = []
reload = Reload(path, arguments, env_var)
for path in paths:
  if isUnder(path, paths):
    break
  prettyPrint("Creating observer: %s" % path, styles.CYAN)
  observer = Observer()
  observer.schedule(reload, path, recursive=True)
  observer.start()
  observer.join
  hot.append(observer)

try:
  while True:
    time.sleep(1)
except KeyboardInterrupt:
  if reload:
    reload.kill()
  for obs in hot:
    obs.stop()
  prettyPrint("Graceful exit", styles.CYAN, True)
# for obs in hot:
#   obs.join()
