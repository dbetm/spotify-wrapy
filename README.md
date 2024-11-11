# Spotify WraPy

[English](README.md) / [Español](README.es.md)

Enjoy your Spotify experience by generating a personalized video showcasing your streaming statistics. This video includes several insightful charts:

- Plays per Hour, Month and Weekday: Visualize your listening habits throughout the day and your weekly and monthly listening patterns.
- Top Songs and Peak Listening Hours: Discover your favorite tracks and when you listen to them most.

Additionally, the video provides comprehensive statistics, such as:

- Total Play Time: Displayed in days, hours, and minutes.
- Total Playbacks: The overall number of songs you've played.
- Skipped Songs: Tracks you've skipped during playback.
- Unique Artists and Songs: The diversity of your listening choices.

![](assets/plays_per_month.png)


## Download your data from Spotify
_Updated: November 10th 2024_

- In the desktop app, go to the dropdown menu where your profile picture is and select the **Account** option.
- Choose **Account privacy**.
- In the **Download your data** section, pick the **Account data** option.
- Click on **Request data**.
- In 5-10 days, they'll send the data to your email (the one linked to your Spotify account).
- Click the "Download" button. A `.zip` file will be downloaded.
- Unzip the file and you'll get a folder called **my_spotify_data** with your data inside.

---------------

## Setup project

**Requirements**

- Git
- Python 3.8 or later.

**Download the repository**
```bash
git clone https://github.com/dbetm/spotify-wrapy.git
```

**Move to the repo folder**

```bash
cd spotify-wrapy
```

**Install required Python libraries**

```bash
make install
```

Note: This will create a python virtual environment.

------------------------

## Create my Spotify WraPy video

1) In the folder with your data, look for the files named something like `StreamingHistory.json`. It could be only one, example: `StreamingHistory0.json`.
2) Copy those files and paste them into the `spotify_data/` folder inside the repository.
3) Activate the virtual environment, if you haven't done so already.
```bash
source .venv/bin/activate
```
4) In the command line, run:
```bash
python3 app.py
```
It also supports Spanish language: `python3 app.py --lang spanish`. If this argument is not passed, it will default to English.

Alternatively, you can pass a start and end date to limit the data used, for example:
```bash
python3 app.py --lang english --start-date 2022-01-13 --end-date 2023-01-01
```
If you don't want to generate a video:
```bash
python3 app.py --lang english --no-video
```
5) The results will be saved in a folder (named according to the datetime of execution) inside the [output](output/) folder.


**Important note**: The timestamp provided by Spotify uses UTC time. By default, this project calculates the timezone of the computer it's run on; you can use a different timezone by running:

```bash
python3 app.py --tz America/New_York
```

You can find the list of timezones at [Wikipedia](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

------------------


## Contribute

This is a non-profit project, made just for fun :) It is not associated with Spotify in any official way.

There are some possible improvements, including generating more charts or with customizable styles. Feel free to contribute:
- Fork the repository.
- Create a new branch from the `main` branch.
- Push your branch and open a Pull Request targeting this repository.
