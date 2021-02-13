<p align="center">LOGO COMES HERE</p>
<h2 align="center" style="border-bottom: none;"><b>Ritsu</b></h2>
<h4 align="center">A Discord bot to fetch anime info from IRC bots and also notify users of new episodes.</h4>

<p align="center">
<span>[SERVER INVITE]</span>
<a href="http://apache.org/licenses/LICENSE-2.0" alt="License: Apache"><img src="https://img.shields.io/badge/License-Apache%202.0-blue" /></a>
<img src="https://img.shields.io/badge/Python-3.9+-green" />
</p>
<hr />

<hr />

**ARCHIVED FOR FUTURE CODE REFERENCE**

<hr />

## Features
- Fetching release schedule of anime[follows the schedule of [SubsPlease](https://subsplease.org)]
- Fetching the packinfo of the last released episode of any anime in a given resolution(480p/720p/1080p).
- Notifying the user when a new episode gets released by sending a message via DM in discord.

  User can choose their required resolution to get the packinfo of that episode in the DM.

<h2>How-to-use<br/>
(For people trying to self-host the bot/Making a different version of bot)
</h2>

> Using the bot which is hosted by me is preferred but writing the steps here nevertheless.
>
> Though, keep in mind that no support would be provided from my side for the self-hosted/forked versions of the bot.

This code is written to work in Python 3.8 or above and uses [discord.py](https://github.com/rapptz/discord.py) library.

Some part of the code uses Linux(more specifically GNU/Linux as some grep arguments are different in different \*nixes) commands like grep and sed.
> People who want to use this code on other platforms are free to do so by forking this repo and changing the code to use a python-port of grep/sed or some other equivalent.
>
> I used grep and sed as it's more efficient and faster and some stuff are annoying to code with just `open()` and `write()` functions in python.

Make your own changes and then...

- A token needs to be obtained by creating a discord bot in Discord [dev-portal](https://discord.com/developers/applications) and should be pasted in a file called `config.py` in [ritsu](https://github.com/supershadoe/ritsu/tree/master/ritsu) folder.
  > Refer [this page](https://discordpy.readthedocs.io/en/latest/discord.html) for more info.
  >
  > An [example](https://github.com/supershadoe/ritsu/blob/master/ritsu/config.py.example) config.py file has been placed in that folder to refer to.
- And the requirements in [requirements.txt](https://github.com/supershadoe/ritsu/blob/master/requirements.txt) should be downloaded by using pip.
  Type the following in the terminal:
  ```bash
  $ pip install -r requirements.txt
  ```
- And launch the bot by typing `python launch.py` or `./launch.py`[while being in that folder].

And voila! The bot is up and running!

> A discord bot is self-hosted and not hosted by discord servers.
>
> Thus, developers need to run it on their PC 24/7 or use something like a Raspberry PI or use cloud to host it. Google about it for more info.

## Issues and PRs
Obviously you can't send a PR to an archived repo...

## License
This app is licensed under Apache License, Version 2.0.
A copy of this license can be found in the [LICENSE](https://raw.githubusercontent.com/supershadoe/ritsu/master/LICENSE) file.
