# sentry-bot

Autonomous Nerf turret

## Setup

1. Install the sentry-bot package
2. _optional_ Make a `config.toml` file, with these contents, in the directory you will run the app from

   ```toml
   VIDEO_PATH='/path/to/any/video.mp4'
   ```

3. Run the webserver with `flask --app sentrybot --debug run`
4. Go to `localhost:5000/`
