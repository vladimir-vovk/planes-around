# -*- coding: utf-8 -*-
import logging
import logging.config
import os
import sys
import subprocess
import tempfile
import requests

import folium
from geopy.distance import vincenty

from planes_around.conf import LOGGING, API_URL, LOCATION_API_URL, BY_NAME_API_URL

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def _open_browser(url):
    if sys.platform == 'win32':
        os.startfile(url)
    elif sys.platform == 'darwin':
        subprocess.Popen(['open', url])
    else:
        try:
            subprocess.Popen(['xdg-open', url])
        except OSError:
            print('Please open a browser on: {}', url)


def show_map(lat, lng, name, data):
    '''Shows map in selected location with planes data.

    Args:
        lat (float): Latitude in degrees
        lng (float): Longitude in degrees
        name (str): Place/city name
        data (list): List of planes data to display on map
    '''
    m = folium.Map(location=[lat, lng], zoom_start=7, tiles='Stamen Terrain')
    summary = '{}<br/>Total planes: {}'.format(name, len(data))
    folium.CircleMarker(location=[lat, lng], popup=summary, fill=True, fill_color='#3186cc').add_to(m)

    for info in data:
        summary = ('callsign: {callsign}<br/>country: {country}<br/>lat: {lat} deg, '
                   'lng: {lng} deg<br/>velocity: {velocity} m/s<br/>distance: {distance:.2f} km<br/>'
                   'heading: {heading} deg from north<br/>on the ground: {on_ground}'.format(**info))
        folium.Marker(location=[info['lat'], info['lng']], popup=summary, icon=folium.Icon(icon='plane')
        ).add_to(m)

    filename = os.path.join(tempfile.gettempdir(), 'planes-around-map.html')
    m.save(filename)
    _open_browser(filename)


def get_location_by_name(name):
    '''Returns information about the location by it's name.

    Args:
        name (str): The name of the location

    Returns:
        dict {'lat' (float): Latitude in degrees,
              'lng' (float): Longitude in degrees,
              'name' (str): Location name,
              'country (str): Location country
    }

    Raises:
       requests.HTTPError if error in request occurred.
       json.JSONDecodeError if error while parsing json occurred.
       AssertionError if no data was received from service.
    '''
    logger.debug('Getting location by name...')
    response = requests.get(BY_NAME_API_URL.format(name))
    if not response.ok:
        logger.error('Response status code from service {} = {}'.format(
            BY_NAME_API_URL, response.status_code))
        response.raise_for_status()

    data = response.json()
    if not data:
        message = 'No data received from {}!'.format(LOCATION_API_URL)
        logger.error(message)
        raise AssertionError(message)

    logger.debug('Location by name successfully retrieved: {}'.format(data))

    try:
        loc = data['results'][0]['geometry']['location']
        city = data['results'][0]['address_components'][0]['long_name']
        country = data['results'][0]['address_components'][-1]['long_name']
    except Exception:
        message = 'Can\'t get information about location!'
        logger.error(message)
        raise AssertionError(message)

    return {'lat': loc['lat'], 'lng': loc['lng'], 'country': country, 'city': city}


def get_user_location():
    '''Returns information about the user location.

    Returns:
        dict {'lat' (float): Latitude in degrees,
              'lng' (float): Longitude in degrees}

    Raises:
       requests.HTTPError if error in request occurred.
       json.JSONDecodeError if error while parsing json occurred.
       AssertionError if no data was received from service.
       ValueError if cant convert received lan/lng to float.
    '''
    logger.debug('Getting user info...')
    response = requests.get(LOCATION_API_URL)
    if not response.ok:
        logger.error('Response status code from service {} = {}'.format(
            LOCATION_API_URL, response.status_code))
        response.raise_for_status()

    data = response.json()
    if not data or 'loc' not in data or not data['loc']:
        message = 'No data received from {}!'.format(LOCATION_API_URL)
        logger.error(message)
        raise AssertionError(message)

    logger.debug('User info successfully retrieved: {}'.format(data))

    loc = data['loc'].split(',')
    try:
        lat = float(loc[0])
    except ValueError:
        message = 'Can\'t convert latitude to float!'
        logger.error(message, exc_info=True)
        raise ValueError(message)

    try:
        lng = float(loc[1])
    except ValueError:
        message = 'Can\'t convert longitude to float!'
        logger.error(message, exc_info=True)
        raise ValueError(message)

    return {'lat': lat, 'lng': lng, 'country': data.get('country'),
            'region': data.get('region'), 'city': data.get('city')}


def filter_data(data, lat, lng, radius):
    '''Returns only data that matches the search criteria.

    Args:
        lat (float): Latitude in degrees.
        lng (float): Longitude in degrees.
        radius (float): Search radius in kilometers.

    Returns:
        The data filtered by the selected parameters. Adds calculated distance to the data vector.
    '''
    logger.debug('Filtering data...')
    valid_data = filter(lambda vec: all([vec[6], vec[5], len(vec) == 17]), data)
    valid_data = map(lambda vec: [*vec, vincenty((lat, lng), (vec[6], vec[5])).km], valid_data)
    return filter(lambda vec: vec[-1] <= radius, valid_data)


def get_data():
    '''Get data about planes from OpenSky service.
    https://opensky-network.org/apidoc/rest.html

    Returns:
       Data about all planes from OpenSky service.

    Raises:
       requests.HTTPError if error in request occurred.
       json.JSONDecodeError if error while parsing json occurred.
       AssertionError if no data was received from service.
    '''
    logger.debug('Getting data from OpenSky...')
    response = requests.get(API_URL)
    if not response.ok:
        logger.error('Response status code from service {} = {}'.format(
            API_URL, response.status_code))
        response.raise_for_status()

    data = response.json()
    if not data:
        message = 'No data received from {}!'.format(API_URL)
        logger.error(message)
        raise AssertionError(message)

    logger.debug('Data successfully received.')
    logger.debug('response data = {}'.format(data))

    return data


def get_data_for_location(lat, lng, radius):
    '''Get data about planes from OpenSky service for specified location and radius.
    https://opensky-network.org/apidoc/rest.html

    Args:
        lat (float): Latitude in degrees.
        lng (float): Longitude in degrees.
        radius (float): Search radius in kilometers.

    Returns:
        The data filtered by the selected parameters. Adds calculated distance to the data vector.

    Raises:
       requests.HTTPError if error in request occurred.
       json.JSONDecodeError if error while parsing json occurred.
       AssertionError if no data was received from service.
    '''
    opensky_data = get_data()
    loc_data = filter_data(opensky_data['states'], lat, lng, radius)
    return [{
        'callsign': vec[1],
        'lat': vec[6],
        'lng': vec[5],
        'country': vec[2],
        'on_ground': vec[8],
        'velocity': vec[9],
        'heading': vec[10],
        'distance': vec[-1],
    } for vec in loc_data]
