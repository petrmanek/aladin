import argparse
import os
import ffmpeg
from .aladin import Aladin


def run_aladin_cli():
    parser = argparse.ArgumentParser(
        description='Download weather forecasts from the Aladin model')

    # CLI flags and options
    parser.add_argument('-l', '--list-forecasts', action='store_true',
                        help='prints a list of available forecasts')
    parser.add_argument('--list-params', action='store_true',
                        help='prints a list of available parameters and their descriptions')
    parser.add_argument('-a', '--all-forecasts', action='store_true',
                        help='retrieves all available forecasts')
    parser.add_argument('-m', '--movie', action='store_true',
                        help='uses ffmpeg to generate mp4 movie for each param')
    parser.add_argument('--movie-framerate', default=2,
                        help='frame rate used for movie, equal to 2 by default')
    parser.add_argument('--legacy-radar', action='store_true',
                        help='uses legacy radar visualization')
    parser.add_argument('-f', '--forecast', nargs='+', default=[],
                        help='forecasts to retrieve')
    parser.add_argument('-p', '--param', nargs='+', default=[],
                        help='forecasted parameters to retrieve, possible options include: ["T2m", "prec", "v10mmslp", "nebul", "nebulb", "nebulm", "nebulh", "RH2m", "veind", "Tmxmn", "prec24"]')
    parser.add_argument('-r', '--range', nargs='+', default=[],
                        help='forecast range to retrieve (in hours), possible options are increments of 3 from 0 to 72')

    args = parser.parse_args()
    al = Aladin()

    if args.list_forecasts:
        # We will retrieve a list of forecasts
        forecasts = al.list_forecasts()

        for forecast in forecasts:
            print(forecast)
    elif args.list_params:
        # We will retrieve a list of params
        params = al.list_params()
        for param, description in params.items():
            print(f'{param:10} - {description}')
    else:
        # We will retrieve picture for forecast(s)

        # Determine what forecasts
        if args.all_forecasts:
            forecasts = al.list_forecasts()
        else:
            # Use forecasts specified by the user
            forecasts = [int(forecast) for forecast in args.forecast]
            if not forecasts:
                # If no forecast is specified, download the latest one
                forecasts = [max(al.list_forecasts())]

        # ...and what ranges
        ranges = [f'{int(str_rng):02}' for str_rng in args.range]

        # Then just go one by one and download them
        for forecast in forecasts:
            forecast_ranges = list(ranges)
            if not forecast_ranges:
                forecast_ranges = al.list_ranges(forecast)

            for param in args.param:
                for rng in forecast_ranges:
                    save_frame_path = f'{forecast}_{param}_{rng}.png'
                    print(
                        f'{{ param={param}, range={rng}, forecast={forecast} }} --> {save_frame_path}')

                    # Here the download actually happens:
                    with open(save_frame_path, 'wb') as out_file:
                        retrieved = al.retrieve(
                            param, forecast, rng, args.legacy_radar, out_file)

                    if not retrieved:
                        # Remove a file that was not filled
                        os.remove(save_frame_path)

                if args.movie:
                    # Generate a movie for every param
                    save_frame_glob = f'{forecast}_{param}_*.png'
                    save_movie_path = f'{forecast}_{param}.mp4'
                    (
                        ffmpeg
                        .input(save_frame_glob, pattern_type='glob', framerate=args.movie_framerate)
                        .output(save_movie_path)
                        .overwrite_output()
                        .run()
                    )
