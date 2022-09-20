# sentry-bot

Autonomous Nerf turret

## Setup

1. Install the sentry-bot package
1. _optional_ Make a `config.toml` file, with these contents, in the directory you will run the app from

   ```toml
   VIDEO_PATH='/path/to/any/video.mp4'
   ```

1. _optional_ Build webGL project with Unity and copy the Build, StreamingAssets and TemplateData directories to sentrybot/static. This game can be accessed via the /game URL.
1. Run the webserver with `flask --app sentrybot --debug run`
1. Go to `localhost:5000/`
