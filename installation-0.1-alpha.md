# Instructions for how to get v0.1-alpha working
**NB:** This isn't in 'master', so YMMV.

First up. This is not an .exe that you can run and you are done.
In order to go past this point, you should be familiar with Github, repo cloning, Linux terminal, and editing files. \
I'm going to be advising you to work from within a virtual Python environment. If you do: great. If you don't: that's on you.

Ok. You're still reading, you want to do this. Great. Here's what you do:

Things you will need:
* A Linux environment - I tested in Ubuntu 22.04.2 LTS, within WSL2
* Python - I tested in 3.10.2
* A virtual Python environment - I recommend you don't skip this
* Some Python libraries. Either in your virtual python environment (recommended), or installed locally (you accept risking your own dependancies)
* file `secrets.py` - this contains your Bluesky userid (for authentication with the API) and your application password. Yes, you can use your BSky pwd. No, you shouldn't.
* file 'bsky_analyzer.py` - the main bad-boy
* the know-how to run a `.py` from CLI and pass in switches

# Let's do this
\[ open your terminal. Create your folder where you are going to run this from, and `cd` into it ]

## First, get your packages installed
```
sudo apt update
sudo apt install python3 python-is-python3 python3-virtualenv python3-pip git wget
```
## Now pull down this branch from this repo
```
git clone https://github.com/mcbazza/bsky_analyzer/ --branch 0.1-alpha
cd bsky_analyzer
chmod +x bsky_analyzer.py
```
## Let's create the virtual Python environment and install the libs

```
# Create the virtual environment within the folder 'env'
python3 -m venv env

# Now, active it
source env/bin/activate

# Now that we are within the virtual python enviornment we can install the libs
pip install atproto argparse numpy datetime

# We need ascii-graph, but the PyPI version isn't maintained and has a bug. This version fixes that:
pip install https://github.com/nyurik/py-ascii-graph/archive/refs/heads/fix-python310.zip
```
## Set your user/pass in secrets.py
Edit `secrets.py` using your editor of choice. And save it.

## Now we can try running it
` ./bsky_analyzer.py -n [accountname]`
Replace [accountname] with the profile name, without the '@'

e.g. for the account https://bsky.app/profile/bsky.app the accountname is `bsky.app` \
`./bsky_analyzer.py -n bsky.app`

For accounts using a custom domain, it's the same. \
e.g. for https://bsky.app/profile/atproto.com the accountname is `atproto.com` \

That's it. \
Let me know if you get any problems with the setup, and once I iron them out I'll commit to 'master' and release a `0.1` version.

Thanks, \
Bazza \
https://bsky.app/profile/mcbazza.com


