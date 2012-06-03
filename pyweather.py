#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree
import urllib.request
import collections


"""Simple weather (from Google) parser."""


class WeatherParser:

    WEATHER_URL = 'http://www.google.com/ig/api?weather={city}&hl=' + \
            '{lang}&oe=UTF-8'

    def __init__(self, city, lang='en'):
        with urllib.request.urlopen(
                self.WEATHER_URL.format(city=city, lang=lang)) as xmlsock:
            self.tree = xml.etree.ElementTree.parse(xmlsock)

    def parse_temp(self, units='c'):
        """Parse temperature in proper units and return a string with
        the temperature.
        """
        return self.parse_current_conditions()['temp_{}'.format(units)]

    def parse_conditions(self):
        """Parse current conditions and return a string"""
        return self.parse_current_conditions()['condition']

    def parse_current_conditions(self):
        """Parse all informations about current weather and returns
        a dictionary.
        Optional argument ignore is a list specifying which tags
        have to be deleted.
        """
        cond_elem = self.tree.find('.//current_conditions')
        conds = {node.tag: node.attrib['data'] for node in cond_elem}
        return conds

    def _parse_forecast_conditions(self, today=False):
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

    def parse_next_days(self):
        return self._parse_forecast_conditions()

    def parse_all(self):
        return self._parse_forecast_conditions(True)


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print('Usage: {0} <city>')
        sys.exit(1)
    we = WeatherParser(sys.argv[1])
    temp = we.parse_temp('c')
    cond = we.parse_conditions()
    print('{0}°C, {1}'.format(temp, cond))
