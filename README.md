# Python hotreload

It observes file changes in directories and reloads scripts or executables.  
Written in python, tested only on os x and python 3 but might work on windows.

### Installation

For now just put the hotreload.py in same directory as the script you want to reload  
In case you encounter permission errors, it's possible that hotreload file needs executing rights:

```
  chmod +x hotreload.py
```

### Usage

Hotreload runs scripts with optional arguments and environment variables.  
For example:

```
./hotreload.py script.py arg1 arg2 -e envK1=envV1 envK2=envV2
```

### Options

| command       | description                           | default |
| ------------- | ------------------------------------- | ------- |
| path          | Required path to reloadable script    |         |
| args          | Arguments for reloadable              |         |
| -e, --env-var | Environment variables for reloadable  |         |
| -I, --Include | Directories to watch                  | ./      |
| -c, --command | Custom command to run reloadable with |         |
| -q, --quiet   | Log only essential info               | False   |
| -s, --silent  | No logging                            | False   |
