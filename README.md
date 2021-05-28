# Python hotreload

It observes file changes in directories and reloads scripts or executables

- [Python hotreload](#python-hotreload)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Options](#options)

### Installation

For now just put the file in same directory as the script you want to reload  
In case you encounter permission errors, it's possible that hotreload file needs executing rights:

```
  chmod +x hotreload.py
```

### Usage

It's possible to run scripts with arguments and environment variables

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
