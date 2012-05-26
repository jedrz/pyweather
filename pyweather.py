#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree
import urllib.request


"""Simple weather (from Google) parser."""


class BaseError(Exception):
    """Base Error in this module"""
    pass


class UnitsError(BaseError):
    """This exception is raised, when units is not correct value"""
    pass


class WeatherParser:

    WEATHER_URL = 'http://www.google.com/ig/api?weather={city}&hl='
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
        temp_elem = self.tree.find('.//temp_{}'.format(self.units))
        temp = temp_elem.attrib['data']
        return temp

    def parse_conditions(self):
        """Parses current conditions and returns string"""
        cond_elem = self.tree.find('.//condition')
        cond = cond_elem.attrib['data']
        return cond

    def parse_current_conditions(self, ignore=["icon"]):
        """Parses all informations about current weather and returns
        dictionary.
        Optional arguments ignore is a list and says, which keys method
        have to delete.
        """
        conditions = self.xmldoc.getElementsByTagName("current_conditions")[0]
        conditions = dict([(cond.nodeName, cond.attributes["data"].value) \
                for cond in conditions.childNodes])
        units_dict = {"c": "f", "f": "c"}
        del conditions["temp_" + units_dict[self.units]]
        for ign in ignore:
            del conditions[ign]
        return conditions

    def _parse_forecast_conditions(self, today=False, ignore=[]):
        """Protected method.

        Returns dictionary with conditions on next days, when optional
        argument is False or also with current day, when Today is True.
        Argument ignore is a list, which has ignored tags.
        """
        forecast = {}
        begin = 0 if today else 1
        for day in self.xmldoc.getElementsByTagName(
                "forecast_conditions")[begin:]:
            day_name = day.firstChild.attributes["data"].value
            forecast[day_name] = {}
            for node in day.childNodes[1:]:
                if node.nodeName not in ignore:
                    forecast[day_name][node.nodeName] = \
                            node.attributes["data"].value
        return forecast

    def parse_weather_on_next_days(self, ignore=["icon"]):
        return self._parse_forecast_conditions(ignore=ignore)

    def parse_all(self, ignore=["icon"]):
        return self._parse_forecast_conditions(True, ignore)


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: {0} <city>")
        sys.exit(1)
    we = WeatherParser(sys.argv[1])
    temp = we.parse_temp().encode("UTF-8")
    cond = we.parse_conditions().encode("UTF-8")
    print("{0}°C, {1}".format(temp, cond))
