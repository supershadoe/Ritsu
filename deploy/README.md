### Files for deployment

In .gitignore, there is a line called `# Ignore .deploy`. That folder is an
exact 1:1 copy of this folder but with all relevant values filled in/modified
as needed.

It holds all the files necessary to deploy the bot (other than the main python
file).

A brief explanation of the files and usage are as follows.

- [env](env) - File used to store all environment variables in a `key=value`
  format. This can be used in multiple ways.
  - In plain shell,
    ```sh
    set -a  # exports all variables set after this

    . .deploy/env
    # equivalent to `source .deploy/env`
    # (loads .env as "config file"/rcfile)

    set +a  # disables that behaviour and reverts back to normal
    ```

  - In a systemd service ([see example here](ritsu-bot.service)),

    In the example systemd unit linked above, you can set your own
    `EnvironmentFile` which can be then loaded by systemd (should be in
    `key=value` format)

  - Changing the [`__main__.py`](../ritsu/__main__.py) file and using
    python-dotenv,

    I personally don't want to add another dependency/module and thus, didn't
    use it but you are free to do whatever. (Also, setting bot secrets can be

- [ritsu-bot.service](ritsu-bot.service) - The name of the service can be
  modified however you want.

  This file can be copied to the hidden deploy folder and edited to match your
  file paths and symlinked to `~/.config/systemd/user/ritsu-bot.service`.

  Then, it can be initialized with
  ```sh
  systemctl --user daemon-reload
  systemctl --user start ritsu-bot
  ```

  > Note: This file can also be used by copying directly to
    `/etc/systemd/system` or `/etc/systemd/user` or even be copied directly to
    `~/.config/systemd/user`.

  > I don't copy the unit file to
  > - `system` due to not wanting to run bot as root.
  > - `user` in `etc` because it's not a service needed by all users.
  > - `user` in `home` directly because I like all my project files to stay
      contained in one folder.
