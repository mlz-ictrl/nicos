#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************
"""NICOS GUI PGAI collision calculations."""

from __future__ import absolute_import, division, print_function

import math

import numpy as np


class Object2D:
    """2D base class."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def pos(self):
        return self.x, self.y

    def moveto(self, x, y):
        self.x = x
        self.y = y

    def rect(self):
        return [self.x, self.y, 0, 0]


class Circle(Object2D):
    """Circle class."""

    def __init__(self, x, y, r):
        Object2D.__init__(self, x, y)
        self.r = r

    def isInside(self, obj):
        if isinstance(obj, Rectangle):
            for c in obj.path():
                n = np.linalg.norm(c - [self.x, self.y])
                if n > self.r:
                    return False
            return True
        return False

    def radius(self):
        return self.r

    def rect(self):
        return [self.x - self.r, self.y - self.r, 2 * self.r, 2 * self.r]


class Rectangle(Object2D):
    """Rectangle class parallel to the axes."""

    def __init__(self, x, y, w, h, rotation=0):
        Object2D.__init__(self, x, y)
        self.w = w
        self.h = h
        self.rotation = rotation

    def rect(self):
        return [self.x - self.w / 2., self.y - self.h / 2., self.w, self.h]

    def path(self):
        x0, y0, w, h = self.rect()
        origin = [self.x, self.y]
        coord = np.array([(x0, y0), (x0 + w, y0), (x0 + w, y0 + h),
                          (x0, y0 + h)]) - origin
        if self.rotation:
            coord = np.array([self.rotatePoint(xy, self.rotation)
                              for xy in coord])
        return coord + origin

    def rotatePoint(self, xy, rotation):
        theta = math.radians(rotation)
        # https://en.wikipedia.org/wiki/Rotation_matrix#In_two_dimensions
        cos_theta, sin_theta = math.cos(theta), math.sin(theta)

        return (
            xy[0] * cos_theta - xy[1] * sin_theta,
            xy[0] * sin_theta + xy[1] * cos_theta,
        )

    def isInside(self, obj):
        if isinstance(obj, Rectangle):
            x0, y0, w, h = self.rect()
            for c in obj.path():
                x, y = c - [self.x, self.y]
                if not x0 <= x <= x0 + w or not y0 <= y <= y0 + h:
                    return False
            return True
        return False


class Square(Rectangle):
    """Square class paralless to the axes."""

    def __init__(self, x, y, w, rotation=0):
        Rectangle.__init__(self, x, y, w, w, rotation)


class Cylinder:
    """Cylinder class."""

    def __init__(self, x, y, r, height):
        self.h = height
        self.circle = Circle(x, y, height)


class Cuboid:
    """Cuboid class."""

    def __init__(self, x, y, z, width, thickness, height):
        self.h = height
        self.z = z
        self.rectangle = Rectangle(x, y, width, thickness)

    def path(self):
        return self.rectangle.rect()


class Cube(Cuboid):
    """Cube class."""

    def __init__(self, x, y, length):
        Cuboid.__init__(self, x, y, length, length, length)


def circle_values(r, cl=3, space=2):
    """Calculate the maximum number of squares in a circle."""
    circle = Circle(0, 0, r)
    square = Square(0, 0, cl)

    def calc_1(r, cl, space):
        pos = []
        m = (cl + space) / 2.
        for y in np.arange(m, circle.radius(), 2 * m):
            for x in np.arange(m, circle.radius(), 2 * m):
                square.moveto(x, y)
                if circle.isInside(square):
                    pos.append([y, x])
                    pos.append([-y, x])
                    pos.append([-y, -x])
                    pos.append([y, -x])
        return pos

    def calc_2(r, cl, space):
        pos = []
        m = cl + space
        y = 0
        for x in np.arange(0, circle.radius(), m):
            square.moveto(x, y)
            if circle.isInside(square):
                pos.append([x, y])
                if x != 0:
                    pos.append([-x, y])
                    pos.append([y, x])
                    pos.append([y, -x])
        for y in np.arange(m, circle.radius(), m):
            for x in np.arange(m, circle.radius(), m):
                square.moveto(x, y)
                if circle.isInside(square):
                    pos.append([y, x])
                    pos.append([-y, x])
                    pos.append([-y, -x])
                    pos.append([y, -x])
        return pos

    cpos_1 = calc_1(r, cl, space)
    cpos_2 = calc_2(r, cl, space)
    return cpos_1 if len(cpos_1) > len(cpos_2) else cpos_2


def rectangle_values(w, h, rot, cl=3, space=2):
    """Calculate the maximum number of squares in a rotated rectangle."""
    rect = Rectangle(0, 0, w, h)
    square = Square(0, 0, cl, 45.)
    r = square.path()
    cl = abs(max([x for x, y in r]) - min([x for x, y in r]))
    d = space / math.cos(math.radians(45))
    nw = int((w + d) / (cl + d))
    nh = int((h + d) / (cl + d))
    woffs = w / 2. - (nw * (cl + d) - d)
    hoffs = h / 2. - (nh * (cl + d) - d)
    wsteps = np.arange(woffs, w / 2., (cl + d))
    hsteps = np.arange(hoffs, h / 2., (cl + d))
    pos = []
    for y in hsteps:
        for x in wsteps:
            square.moveto(x, y)
            if rect.isInside(square):
                pos.append(list(rect.rotatePoint([x, y], -rot)))
    return pos


def cuboid_values(w, thickness, height, rot, cl=3, space=2):
    """Calculate the maximum number of cells in a rotated cuboid."""
    pos = [
        [113.97 - 100, 99.27 - 100, 61.89 - 30.],
        [113.97 - 100, 99.27 - 100, 70.18 - 30.],
        [105.47 - 100, 90.77 - 100, 45.31 - 30.],
        [105.47 - 100, 90.77 - 100, 53.60 - 30.],
        [105.47 - 100, 90.77 - 100, 61.89 - 30.],
        [105.47 - 100, 90.77 - 100, 70.18 - 30.],
        [105.47 - 100, 90.77 - 100, 78.47 - 30.],
        [105.47 - 100, 90.77 - 100, 86.76 - 30.],
        [96.97 - 100, 82.27 - 100, 45.31 - 30.],
        [96.97 - 100, 82.27 - 100, 53.60 - 30.],
        [96.97 - 100, 82.27 - 100, 61.89 - 30.],
        [96.97 - 100, 82.27 - 100, 70.18 - 30.],
        [96.97 - 100, 82.27 - 100, 78.47 - 30.],
        [96.97 - 100, 82.27 - 100, 86.76 - 30.],
        [88.47 - 100, 73.77 - 100, 61.89 - 30.],
        [88.47 - 100, 73.77 - 100, 70.18 - 30.],
        [98.72 - 100, 89.07 - 100, 37.02 - 30.],
    ]
    cpos = rectangle_values(w, thickness, rot, cl, space)
    pos = []
    for x in height_steps(height, cl, space):
        for v in cpos:
            pos.append(v + [x])
    return pos


def height_steps(h, cl=3, space=2):
    """Calculate the maximum number of cells in height."""
    n = int((h + space) / (cl + space))
    offs = (h - n * (cl + space) + space) / 2. + cl / 2.
    steps = np.arange(offs, h, (cl + space))
    return steps


def cylinder_values(r, h, cl=3, space=2):
    """Calculate the maximum number of cells in a cylinder."""
    cpos = circle_values(r, cl, space)
    pos = []
    for x in height_steps(h, cl, space):
        for v in cpos:
            pos.append(v + [x])
    return pos


def sphere_values(r, cl=3, space=2):
    """Calculate the maximum number of cells in a sphere."""
    pos = []
    cpos_1 = []
    cpos_2 = []
    if r >= (cl + space / 2.):
        cpos_1 = circle_values(math.sqrt(r * r - (cl + space / 2.) ** 2), cl,
                               space)
    if r >= cl:
        cpos_2 = circle_values(math.sqrt(r * r - (cl * cl / 4)), cl, space)
    if len(cpos_1) > len(cpos_2):
        m = 2 * cl + 1.5 * space
        h = (cl + space) / 2
        for p in cpos_2:
            pos.append(p + [r + h])
            pos.append(p + [r - h])
    else:
        m = 1.5 * cl + space
        for p in cpos_2:
            pos.append(p + [r])

    for h in np.arange(m, r, (cl + space)):
        if h <= r:
            radius = math.sqrt(r * r - h * h)
            cpos = circle_values(radius, cl, space)
            for v in cpos:
                pos.append(v + [r + (h - cl / 2.)])
                pos.append(v + [r - (h - cl / 2.)])
    return pos
