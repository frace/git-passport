# What is git-passport?
A Git pre-commit hook which lets us select a local ID from a predefined set of
git identities.


## Get it!
```
>:mkdir -p ~/.git/hooks/bin && cd $_
>:git clone git://github.com/frace/git-passport.git
>:chmod +x ./git-passport/git-passport.py
>:_
```


## Installation
There are many ways to handle your hooks. What I do in oder to work with
multiple hooks is the following solution:
```
>:mkdir -p ~/.git/hooks/pre-commit.d && cd $_
>:ln -sf ~/.git/hooks/bin/git-passport/git-passport.py ./00-git-passport
>:mkdir -p ~/.git/templates/hooks && cd $_
>:touch pre-commit && chmod +x $_
>:_
```

Add the Git template directory path into your `~/.gitconfig`:
```
[init]
    templatedir = ~/.git/templates
```

Then in `~/.git/templates/hooks/pre-commit` I put a little bash script which
loads one hook after another:
```
>:cat ~/.git/templates/hooks/pre-commit
#!/usr/bin/env bash

hooks_pre_commit="${HOME}/.git/hooks/pre-commit.d/"

for hook in ${hooks_pre_commit}*; do
    "$hook"
done
>:_
```

Afterwards each `git init` or `git clone` command will distribute
the hook into a new repository.
If you want to apply the hook to already exisiting repos then just run
`git init` inside the repository in order to reinitialize it.


## Configuration
On the first run `git-passport.py` generates a sample configuration file inside
your home directory:
```
>:cd ~/.git/hooks/bin/git-passport
>:./git-passport.py
No configuration file found.
Generating a sample configuration file.

~Done~
>:_
```

The configuration file is rather self-explanatory:
```
>:cat ~/.git_passport
[General]
enable_hook = True
sleep_duration = 1.5

[Passport 0]
email = email_0@example.com
name = name_0
service = github.com

[Passport 1]
email = email_1@example.com
name = name_1
service = gitlab.com
>:_
```

Adjust the existing sections and add as many git IDs as you like by following
the section scheme.


## Bugs
You are welcome to report bugs at the [project bugtracker][project-bugtracker]
at github.com.

[project-bugtracker]: https://github.com/frace/git-passport/issues


* * *
## Credits:
+ Hook idea inspired by [ORR SELLA][related-1]
+ Idea grew at [stackoverflow.com][related-2]

[related-1]: https://orrsella.com/2013/08/10/git-using-different-user-emails-for-different-repositories/
[related-2]: http://stackoverflow.com/questions/4220416/can-i-specify-multiple-users-for-myself-in-gitconfig/23107012#23107012
