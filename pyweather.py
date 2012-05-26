#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
from xml.dom import minidom


class BaseError(Exception):
    """Base Error in this module"""
    pass


class UnitsError(BaseError):
    """This exception is raised, when units is not correct value"""
    pass


class Weather(object):

    WEATHER_URL = "http://www.google.com/ig/api?weather={city}&hl=" + \
            "{lang}&oe=UTF-8"

    def __init__(self, city, lang="pl", units="c"):
        if units not in ("c", "f"):
            raise UnitsError("Units must be c or f, not {0}".format(units))
        self.units = units
        xml = urllib2.urlopen(self.WEATHER_URL.format(city=city,
            lang=lang))
        self.xmldoc = minidom.parse(xml)

    def parse_temp(self):
        """Parses temperature in proper units and returns string with
        temperature.
        """
        temp = self.xmldoc.getElementsByTagName("temp_" + self.units)
        temp = temp[0].attributes["data"].value
        return temp

    def parse_conditions(self):
        """Parses current conditions and returns string"""
        cond = self.xmldoc.getElementsByTagName("condition")
        cond = cond[0].attributes["data"].value
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
