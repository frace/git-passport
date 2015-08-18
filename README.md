# What is git-passport?
git-passport is a Git command and hook written in Python to manage multiple Git
users / user identities.


## Get it!
```
mkdir -p ~/.git/hooks/bin && cd $_
git clone git://github.com/frace/git-passport.git
chmod +x ./git-passport/git-passport.py
```


## Installation
There are many ways to handle your hooks. What I do in order to work with
multiple hooks is the following solution:
```
mkdir -p ~/.git/hooks/pre-commit.d && cd $_
ln -sf ~/.git/hooks/bin/git-passport/git-passport.py ./00-git-passport
mkdir -p ~/.git/templates/hooks && cd $_
touch pre-commit && chmod +x $_
```

Add the Git template directory path into your `~/.gitconfig` and create an
alias in order to be able to execute the script manually as a «native» git
command by invoking `git passport`:
```
[alias]
    passport = !${HOME}/.git/hooks/bin/git-passport/git-passport.py

[init]
    templatedir = ~/.git/templates
```

In `~/.git/templates/hooks/pre-commit` I put a little bash script which
loads one hook after another:
```
#!/usr/bin/env bash

hooks_pre_commit="${HOME}/.git/hooks/pre-commit.d/"

for hook in ${hooks_pre_commit}*; do
    "$hook"
done
```

Afterwards each `git init` or `git clone` command will distribute
the hook into a new repository.
If you want to apply the hook to already exisiting repos then just run
`git init` inside the repository in order to reinitialize it.


## Configuration
On the first run `git-passport.py` generates a sample configuration file inside
your home directory:
```
cd ~/.git/hooks/bin/git-passport
./git-passport.py
   No configuration file found in ~/.
   Generating a sample configuration file.
```

The configuration file `~/.gitpassport` is rather self-explanatory:
```
[general]
enable_hook = True
sleep_duration = 0.5
quiet = False

[passport 0]
email = email_0@example.com
name = name_0
service = github.com

[passport 1]
email = email_1@example.com
name = name_1
service = gitlab.com
```

Setting `quiet` to `True` will stop `git-passport.py` from printing the active passport upon default execution (To see the active passport with `quiet` enabled, you must pass the `-a` option).

Adjust the existing sections and add as many passports as you like by following
the section scheme.


## Usage
If you setup the script as a hook only it will be invoked automatically
during each `git commit` command.
You can pass the following options if you use `git-passport.py` as a Git
command, too:
```
git passport -h
   usage: git passport (--select | --delete | --active | --passports)

   manage multiple Git identities

   optional arguments:
     -h               show this help message and exit
     -s, --select     select a passport
     -d, --delete     delete the active passport in .git/config
     -a, --active     print the active passport in .git/config
     -p, --passports  print all passports in ~/.gitpassport
```


## Bugs
You are welcome to report bugs at the [project bugtracker][project-bugtracker]
at github.com.

[project-bugtracker]: https://github.com/frace/git-passport/issues


* * *
## Credits:
+ Inspired by [ORR SELLA][credits-1]
+ Grew at [stackoverflow.com][credits-2]

[credits-1]: https://orrsella.com/2013/08/10/git-using-different-user-emails-for-different-repositories/
[credits-2]: http://stackoverflow.com/questions/4220416/can-i-specify-multiple-users-for-myself-in-gitconfig/23107012#23107012
[credits-3]: http://codereview.stackexchange.com/questions/76935/python-based-git-pre-commit-hook-to-manage-multiple-users-git-identities
