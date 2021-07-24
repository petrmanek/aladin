Aladin Python CLI
=================

A command-line interface for retrieving hourly forecasts from the "Aladin" model
developed by the [Czech Hydrometeorological Institute][chmi].

|---|---|
| ![](https://github.com/petrmanek/aladin/blob/master/examples/2021072412_nebul.gif?raw=true) | ![](https://github.com/petrmanek/aladin/blob/master/examples/2021072412_T2m.gif?raw=true) |
| ![](https://github.com/petrmanek/aladin/blob/master/examples/2021072412_prec.gif?raw=true) | ![](https://github.com/petrmanek/aladin/blob/master/examples/2021072412_v10mmslp.gif?raw=true) |


## What is this?

Aladin is a weather forecasting system that can predict various weather
parameters (temperature, humidity, clouds, precipitation) in the Czech region
with surprisingly satisfactory accuracy. In its current mode of operation, it
produces forecasts every 6 hours, each comprising 24 prediction points spaced 3
hours apart. This yields prediction horizon of 72 hours.

Recently I caught myself checking the [Aladin website (in
Czech)][aladin-forecasts] way too often. Unfortunately at the time of writing, I
found the frontend not to be too user friendly, so I made this one-day project
that caters to all my forecasting needs.

The Python 3 package in this repository can bypass Aladin's frontend and
download all weather maps directly from the backend as PNG files, which can be
processed in various ways (e.g. to produce a slideshow on your desktop).


## How to use it?

You can use the package in two ways: as a library, or as a command-line tool.


### Library usage

The `aladin` package provides a single class `Aladin` that serves as a client
for the backend. You can use the following instance methods to retrieve things:

 - `list_forecasts()` returns a list of available forecast IDs (ints),
 - `list_params()` returns a dict of forecasted parameters (ID/str:
   human-friendly description/str)
 - `list_ranges(forecast)` returns a list of prediction points (str) for a given
   forecast ID
 - `retrieve(param, forecast, range, legacy_radar, write_buffer)` downloads PNG
   data for a given triple of (forecasted parameter ID, forecast ID, prediction
   point) and writes it to `write_buffer` (which can be a file or any other
   `MemoryIO`), the `legacy_radar` option is a boolean that enables older
   appearance for the `prec` and `prec24` parameters. If the PNG data is
   available, the method returns `True`, otherwise `False`.

If any of the above methods encounters network or other issues, appropriate
errors are raised.


### Command-line usage

List all available forecasts:

```bash
aladin -l
```

Download all prediction points of the latest precipitation forecast:

```bash
aladin -p prec
```

The same thing but also for temperature and relative humidity at 2 meters:

```bash
aladin -p prec RH2m T2m
```

Download only 3-, 6- and 9-hour prediction points of the latest precipitation
forecast:

```bash
aladin -p prec -r 3 6 9
```

Download all prediction points of a specific precipitation forecast:

```bash
# we retrieved "2021072412" earlier using `aladin -l`
aladin -p prec -f 2021072412
```

Download all prediction points of all available precipitation forecasts:

```bash
aladin -p prec -a
```

Download all prediction points of the latest precipitation forecast and use
ffmpeg to concatenate them into a MP4 movie:

```bash
aladin -p prec -m
```

Here's a complete usage string for the command-line tool:

```
usage: aladin [-h] [-l] [--list-params] [-a] [-m] [--movie-framerate MOVIE_FRAMERATE] [--legacy-radar] [-f FORECAST [FORECAST ...]] [-p PARAM [PARAM ...]] [-r RANGE [RANGE ...]]

Download weather forecasts from the Aladin model

optional arguments:
  -h, --help            show this help message and exit
  -l, --list-forecasts  prints a list of available forecasts
  --list-params         prints a list of available parameters and their descriptions
  -a, --all-forecasts   retrieves all available forecasts
  -m, --movie           uses ffmpeg to generate mp4 movie for each param
  --movie-framerate MOVIE_FRAMERATE
                        frame rate used for movie, equal to 2 by default
  --legacy-radar        uses legacy radar visualization
  -f FORECAST [FORECAST ...], --forecast FORECAST [FORECAST ...]
                        forecasts to retrieve
  -p PARAM [PARAM ...], --param PARAM [PARAM ...]
                        forecasted parameters to retrieve, possible options include: ["T2m", "prec", "v10mmslp", "nebul", "nebulb", "nebulm", "nebulh", "RH2m", "veind", "Tmxmn", "prec24"]
  -r RANGE [RANGE ...], --range RANGE [RANGE ...]
                        forecast range to retrieve (in hours), possible options are increments of 3 from 0 to 72
```

## Copyright

This repository was created on July 24-25, 2021 by [Petr Mánek][pm], and is
licensed under the MIT license. Note that this project merely represents an
alternative means of accessing the Aladin system, which is widely available to
the general public. The author makes no claims regarding generated forecasts,
maps and other materials, as these may be subject to other terms and conditions.
For more information about their licensing, please check the [CHMI
website][chmi].


[chmi]: https://www.chmi.cz/?l=en
[aladin-forecasts]: https://www.chmi.cz/files/portal/docs/meteo/ov/aladin/results/ala.html
[pm]: https://petrmanek.cz

