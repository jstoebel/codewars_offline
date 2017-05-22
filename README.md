# Kata Scrape

## What's this for?

I often find myself with small periods of time with nothing to do. Rather than stare at my phone, I prefer to level up my coding skills. [Codewars.com](http://www.codewars.com) is my favorite, but the trouble is that during these periods of down time I often don't have Internet access. Always wanting to plan ahead, I would copy and paste a few katas and work on them on my local machine. That seemed like a silly thing to have to do myself, so I made a tool for it.

## Installation

`pip install kata_scrape`

You will also need:

 - [PhantomJS](http://phantomjs.org/download.html)
 - Runtimes for Python/Ruby/Node depending on which languages you wish to train in.
 - npm if you will be training in Javascript

## Basic Usage

### Start a new katas directory
To begin:

```
kata-scrape init # create a directory called `katas` in current directory
cd katas

# alternatively...
kata-scrape init --dir ~/code # create a katas directory in `~/code`
```

This will create a directory called `katas`. In that directory is a file `config.json`. You'll need to provide your Codewars api key (check in your account settings for this) and the languages you will be training in. For example:

```
{
    "api_key": "<your codewars api key here>",
    "languages": ["python", "ruby", "javascript"]
}

```

Currently the supported languages are Python, Ruby and Javascript.

### Grab a kata

To scrape a kata type `kata-scrape fetch`. A kata will be fetched for you, choosing randomly from one of your specified languages in `config.json`. The command will fetch:

 - a description of the kata
 - the starter code
 - working tests!

To specify a language: `kata-scrape fetch --lang python`
