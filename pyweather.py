#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree
import urllib.request
import collections


"""Simple weather (from Google) parser."""


class BaseError(Exception):
    """Base Error in this module"""
    pass


class UnitsError(BaseError):
    """This exception is raised, when units is not correct value"""
    pass


class WeatherParser:

    WEATHER_URL = 'http://www.google.com/ig/api?weather={city}&hl=' + \
            '{lang}&oe=UTF-8'

    def __init__(self, city, lang='en', units='c'):
        if units not in ('c', 'f'):
            raise UnitsError('UnitsError: {} units are invalid'.format(units))
        self.units = units
        with urllib.request.urlopen(
                self.WEATHER_URL.format(city=city, lang=lang)) as xmlsock:
            self.tree = xml.etree.ElementTree.parse(xmlsock)

    def _find(self, it, tag):
        for i in it:
            res = i.find(tag)
            if res:
                return res
            else:
                return self._find(i, tag)

    def parse_temp(self):
        """Parse temperature in proper units and return a string with
        the temperature.
        """
        return self.parse_current_conditions()['temp_{}'.format(self.units)]

    def parse_conditions(self):
        """Parse current conditions and return a string"""
        return self.parse_current_conditions()['condition']

    def parse_current_conditions(self, ignore=[]):
        """Parse all informations about current weather and returns
        a dictionary.
        Optional argument ignore is a list specifying which tags
        have to be deleted.
        """
        cond_elem = self.tree.find('.//current_conditions')
        conds = {node.tag: node.attrib['data'] for node in cond_elem}
        # remove redundant units
        units_dict = {'c': 'f', 'f': 'c'}
        del conds['temp_' + units_dict[self.units]]
        for ign in ignore:
            del conds[ign]
        return conds

    def _parse_forecast_conditions(self, today=False, ignore=[]):
        """Protected method.

        Return ordered dictionary with conditions on next days, when optional
        argument is False or also with current day, when Today is True.
        Argument ignore says which tags should be removed.
        """
        forecast = collections.OrderedDict()
        begin = 0 if today else 1
        for elem in self.tree.findall('.//forecast_conditions')[begin:]:
            forecast[elem.find('day_of_week').attrib['data']] = \
                    {n.tag: n.attrib['data'] for n in elem}
        return forecast

    def parse_next_days(self, ignore=[]):
        return self._parse_forecast_conditions(ignore=ignore)

    def parse_all(self, ignore=["icon"]):
        return self._parse_forecast_conditions(True, ignore)


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print('Usage: {0} <city>')
        sys.exit(1)
    we = WeatherParser(sys.argv[1])
    temp = we.parse_temp().encode('UTF-8')
    cond = we.parse_conditions().encode('UTF-8')
    print('{0}°C, {1}'.format(temp, cond))
