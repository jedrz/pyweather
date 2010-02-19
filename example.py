#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyweather

we = pyweather.Weather("Siedlce")
print(we.parse_temp())
print(we.parse_conditions())
