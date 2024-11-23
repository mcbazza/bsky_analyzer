# Running via Docker

## Pre-requisites
* You'll need to `cd` to the folder where you are going to store `bsky_analyzer`
* A Bluesky account and application password, so that you can authenticate with the service
* A username to run bsky_analyzer against
* Docker to be installed

## Getting it setup
You're going to need the files from this branch of the repo. \
If you're happy with using Git:
`git clone https://github.com/mcbazza/bsky_analyzer/ --branch 0.1-alpha-docker`

If you don't know about that, but can use wget:
```
wget https://raw.githubusercontent.com/mcbazza/bsky_analyzer/refs/heads/0.1-alpha-docker/Dockerfile
wget https://raw.githubusercontent.com/mcbazza/bsky_analyzer/refs/heads/0.1-alpha-docker/bsky_analyzer.py
```

If you don't know about `wget`, then you'll have to view the above two files in your browser, and save to your folder with the correct names and file extensions.

## Docker Build
```
docker build -f ./Dockerfile -t bsky_analyzer .
```

## Docker Run

You can pass in your user/pass via environment variables. Saves on having to edit the `secrets.py` file.
```
docker run -e 'BSKY_USER=your-bsky-username-here' -e 'BSKY_PWD=your-bsky-app-password-here' -it bsky_analyzer account-to-analyze
```

That's all. Enjoy. Let me know how you get on with it.
