# Remote Gource

This tool pulls commit data from a remote source (e.g. Github, Bitbucket etc) and outputs [a file](https://github.com/acaudwell/Gource/wiki/Custom-Log-Format) which can be ingested by [gource](https://gource.io).

This makes it easier to generate multi-repo Gource outputs based on a team workspace/organisation.

## Usage

```shell
pip install remote-gource
```

## Building & Deploying

TODO.

## How it works (multi-repo)

The Gource [log format](https://github.com/acaudwell/Gource/wiki/Custom-Log-Format) looks like the following.

```
<unix_timestamp>|<committer_name>|<[M]odified/[A]dded/[D]eleted>|<path_to_touched_file>
```

By default, Gource only understands a single branch on a single repo. In order to render "multiple repos", we can concatenate the logs (detailed above) from each repo/branch and transform each line by prepending the repo name to the file path. This emulates one big "virtual" repo with the real repos being subfolders.


On top of this, we can use the `--hide root` [option](https://github.com/acaudwell/Gource/wiki/Controls#hiding-elements) to render each subfolder separately (without a connecting node).

## Configuration

Config is stored at `$XDG_CONFIG_HOME/remote-gource/config.yaml`. See [the default config](./remote_gource/config_default.yaml) for the general structure.

### Bitbucket

1. Create an app password [here](https://bitbucket.org/account/settings/app-passwords/new). Make sure you grant read access to "Workspace membership" and "Projects".
2. Fill out the `client_id`, `client_secret` and `workspace` fields in your config file.


### Github

Not supported yet.
