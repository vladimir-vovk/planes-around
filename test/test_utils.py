# -*- coding: utf-8 -*-
import json
import pytest
import requests
import requests_mock

from planes_around.conf import API_URL, LOCATION_API_URL, BY_NAME_API_URL
import planes_around.utils as utils


def test_get_data_is_service_running():
    assert utils.get_data(), 'No data received from {}!'.format(API_URL)


@requests_mock.Mocker(kw='mock')
def test_get_data_response_not_ok(**kwargs):
    kwargs['mock'].get(API_URL, status_code=400)
    with pytest.raises(requests.HTTPError):
        utils.get_data()


@requests_mock.Mocker(kw='mock')
def test_get_data_no_json(**kwargs):
    kwargs['mock'].get(API_URL, text='not<h1>a</h2>/n/njson--response')
    with pytest.raises(json.JSONDecodeError):
        utils.get_data()


@requests_mock.Mocker(kw='mock')
def test_get_data_empty_response(**kwargs):
    kwargs['mock'].get(API_URL, text='{}')
    with pytest.raises(AssertionError):
        utils.get_data()


def test_get_user_location_service_running():
    loc = utils.get_user_location()
    assert loc, 'No data received from {}!'.format(LOCATION_API_URL)
    assert 'lat' in loc and 'lng' in loc, 'No latitude or longitude in return value!'


@requests_mock.Mocker(kw='mock')
def test_get_user_location_response_not_ok(**kwargs):
    kwargs['mock'].get(LOCATION_API_URL, status_code=400)
    with pytest.raises(requests.HTTPError):
        utils.get_user_location()


@requests_mock.Mocker(kw='mock')
def test_get_user_location_no_json(**kwargs):
    kwargs['mock'].get(LOCATION_API_URL, text='not<h1>a</h2>/n/njson--response')
    with pytest.raises(json.JSONDecodeError):
        utils.get_user_location()


@requests_mock.Mocker(kw='mock')
def test_get_user_location_empty_response(**kwargs):
    kwargs['mock'].get(LOCATION_API_URL, text='{}')
    with pytest.raises(AssertionError):
        utils.get_user_location()


@requests_mock.Mocker(kw='mock')
def test_get_user_location_bad_response(**kwargs):
    kwargs['mock'].get(LOCATION_API_URL, text='{"loc": "some bad, data"}')
    with pytest.raises(ValueError):
        utils.get_user_location()


def test_get_location_by_name_service_running():
    loc = utils.get_location_by_name('Krasnoyarsk')
    assert loc, 'No data received from {}!'.format(BY_NAME_API_URL)
    assert 'lat' in loc and 'lng' in loc, 'No latitude or longitude in return value!'


@requests_mock.Mocker(kw='mock')
def test_get_location_by_name_response_not_ok(**kwargs):
    name = 'Krasnoyarsk'
    kwargs['mock'].get(BY_NAME_API_URL.format(name), status_code=400)
    with pytest.raises(requests.HTTPError):
        utils.get_location_by_name(name)


@requests_mock.Mocker(kw='mock')
def test_get_location_by_name_no_json(**kwargs):
    name = 'Krasnoyarsk'
    kwargs['mock'].get(BY_NAME_API_URL.format(name), text='not<h1>a</h2>/n/njson--response')
    with pytest.raises(json.JSONDecodeError):
        utils.get_location_by_name(name)


@requests_mock.Mocker(kw='mock')
def test_get_location_by_name_empty_response(**kwargs):
    name = 'Krasnoyarsk'
    kwargs['mock'].get(BY_NAME_API_URL.format(name), text='{}')
    with pytest.raises(AssertionError):
        utils.get_location_by_name(name)


@requests_mock.Mocker(kw='mock')
def test_get_location_by_name_bad_response(**kwargs):
    name = 'Krasnoyarsk'
    kwargs['mock'].get(BY_NAME_API_URL.format(name), text='{"loc": "some bad, data"}')
    with pytest.raises(AssertionError):
        utils.get_location_by_name(name)
