#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import sys, os, stat, time, argparse, atexit, subprocess
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
parser.add_argument("-W", "--Watch", nargs='*', type=str, help="Directories to watch, default='./'")
parser.add_argument("-c", "--command", type=str, help="Custom command to run reloadable with")
parser.add_argument("-V", "--Version", help="show application version", action="store_true")
parser.add_argument("-q", "--quiet", help="Log only essential info", action="store_true")
parser.add_argument("-s", "--silent", help="No logs", action="store_true")
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
  if args.silent or args.quiet and not loud:
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
  try:
    if input("Are you sure? (y/n)") != "y":
      return False
    os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
    return True
  except:
    return False

###
## Classes
###
class Hotpot:
  pot = []
  watchPaths = []
  reload = None

  def __init__(self, reload, watch = ['./']):
    self.watchPaths = watch
    self.reload = reload
    self.cook()

  def cook(self):
    if not self.reload or len(self.watchPaths) <= 0:
      raise Exception("Missing ingredients")
    for path in self.watchPaths:
      if isUnder(path, self.watchPaths):
        break
      prettyPrint("Creating observer: %s" % path, styles.CYAN)
      hot = Observer()
      hot.schedule(self.reload, path, recursive=True)
      hot.start()
      hot.join
      self.pot.append(hot)

  def kill(self):
    for hot in self.pot:
      hot.stop()

class Reload(FileSystemEventHandler):
  process = None
  command = None
  path = None
  arguments = None
  env_vars = None
  def __init__(self, path, arguments, env_vars, command=None):
    self.command = command
    self.path = path
    self.arguments = arguments
    self.env_vars = env_vars
    super().__init__()

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
    if self.process:
      self.kill()
      msg = "Reloading"
    subArgs = [self.command, self.path, self.arguments] if self.command else [self.path, self.arguments]
    prettyPrint(msg+" script with command: %s" % " ".join(subArgs), styles.WARNING, True)
    try:
      self.process = subprocess.Popen(subArgs, env=self.env_vars)
    except PermissionError as e:
      prettyPrint("Failed to execute file with permission error", styles.CRITICAL, True)
      if not chmodPrompt(self.path): 
        raise e
    except OSError as e:
      if e.errno != 8:
        raise e
      prettyPrint("Failed to execute file with exec error, try adding '#!/usr/local/bin/python3' or similar top of executable file " , styles.CRITICAL, True)

  def kill(self):
    if self.process:
      self.process.kill()

###
## Variables
###
if args.Version:
  prettyPrint("Python hotreload 1.0", styles.BOLD, True)
  sys.exit(1)

path = parsePath(args.path)
arguments = ' '.join(args.arguments)
env_var = parseEnv(args.env_var)
watchPaths = ['./']
command = args.command
if args.Watch: 
  watchPaths = args.Watch

###
## Info
###
prettyPrint("*** Python hotreloader 1.0 ***", styles.HEADER)
prettyPrint("Reload full path: %s" % path, styles.CYAN)
if command: prettyPrint("Custom command: %s" % command)
prettyPrint("With arguments: %s" % arguments)
prettyPrint("With environment variables: %s" % env_var)
prettyPrint("Watching paths: %s" % watchPaths)

###
## Hotreload
###
reload = Reload(path, arguments, env_var, command)
hotpot = Hotpot(reload, watchPaths)

def gracefulExit(signum=None,frame=None):
  reload.kill()
  hotpot.kill()
  prettyPrint("Graceful exit", styles.CYAN, True)

atexit.register(gracefulExit)
reload.reload()

try:
  while True:
    time.sleep(1)
except KeyboardInterrupt:
  prettyPrint("Good bye!", styles.BLUE)
