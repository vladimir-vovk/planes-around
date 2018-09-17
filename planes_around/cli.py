# -*- coding: utf-8 -*-
import argparse
import signal
import sys
import logging
import logging.config
import json

from planes_around.conf import LOGGING
import planes_around.utils as utils

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

GET_USER_LOCATION_ERROR = 1
GET_LOCATION_BY_NAME_ERROR = 2


def sigint_handler(sig, frame):
    logger.warning('The execution of the program was interrupted by the user!', exc_info=True)
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, sigint_handler)

    parser = argparse.ArgumentParser(
        description='Get info about planes around the specified location using the OpenSky service.\n'
        'By default, the program tries to determine your location by IP address \n'
        'and looks for planes within a radius of 500 km.')
    parser.add_argument('--lat', type=float, default=0, help='Latitude in degrees')
    parser.add_argument('--lng', type=float, default=0, help='Longitude in degrees')
    parser.add_argument('-r', '--radius', type=float, default=500, help='Search planes within a radius (kilometers)')
    parser.add_argument('-n', '--name', type=str, default='', help='The name of the city or place near which you want to search')
    parser.add_argument('--heading', type=float, help='Filter planes by their direction in degrees in respect to the North clockwise')
    parser.add_argument('--heading-delta', type=float, default=0, help='Heading plus/minus a certain number of degrees')
    parser.add_argument('--no-map', action='store_true', help='Don\'t show the map')
    parser.add_argument('--no-map-radius', action='store_true', help='Don\'t display radius circle on the map')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--on-the-ground', action='store_true', help='Show only planes on the ground')
    group.add_argument('--in-the-sky', action='store_true', help='Show only planes in the sky')

    args = parser.parse_args()
    logger.info('✈️')

    if args.lat and args.lng:
        lat = args.lat
        lng = args.lng
        name = ''
    elif args.name:
        logger.info('Getting location for {}...'.format(args.name))
        try:
            loc = utils.get_location_by_name(args.name)
        except Exception:
            logger.error('Error while trying to get location by name!')
            logger.info('Exiting program...')
            exit(GET_LOCATION_BY_NAME_ERROR)

        lat = loc['lat']
        lng = loc['lng']
        name = loc['city']
        logger.info('Found location for {}: {}, {} (lat = {}, lng = {})'.format(
            args.name, loc['country'], loc['city'], lat, lng))
    else:
        logger.info('Location doesn\'t specified.')
        try:
            loc = utils.get_user_location()
        except Exception:
            logger.error('Error while trying to get user location!')
            logger.info('Exiting program...')
            exit(GET_USER_LOCATION_ERROR)

        lat = loc['lat']
        lng = loc['lng']
        name = loc['city'] if loc['city'] else loc['region']
        logger.info('Using you current location: {}, {} (lat = {}, lng = {})'.format(
            loc['country'], name, lat, lng))

    logger.info('Getting data from OpenSky service...')
    opensky_data = utils.get_data()
    logger.info('Filtering data to get planes within a radius of {} km...'.format(args.radius))
    loc_data = utils.filter_data(opensky_data['states'], lat=lat, lng=lng, radius=args.radius,
                                 heading=args.heading, heading_delta=args.heading_delta,
                                 on_the_ground=args.on_the_ground, in_the_sky=args.in_the_sky)

    data = [{
        'callsign': vec[1],
        'lat': vec[6],
        'lng': vec[5],
        'country': vec[2],
        'on_ground': vec[8],
        'velocity': vec[9],
        'heading': vec[10],
        'vertical_rate': vec[11],
        'distance': vec[-1],
    } for vec in loc_data]

    planes_where = ''
    if args.on_the_ground:
        planes_where = 'on the ground '
    if args.in_the_sky:
        planes_where = 'in the sky '

    with_heading = ''
    if args.heading:
        with_heading = ' with heading {} +/- {} degrees'.format(args.heading, args.heading_delta)

    logger.info('Planes found:')
    logger.info(json.dumps(data, indent=4))
    logger.info('Total planes {}within a radius of {} km near {}\n'
                '(lat = {}, lng = {}){}: {}'.format(
                    planes_where, args.radius,
                    '{} '.format(name) if name else '',
                    lat, lng, with_heading, len(data)))
    if not args.no_map:
        radius = None if args.no_map_radius else args.radius
        utils.show_map(lat, lng, name, data, radius)
    logger.info('Done! 🎉')


if __name__ == '__main__':
    main()
