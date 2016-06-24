# Copyright (c) 2015  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
Provides a :class:`Quaternion` class that is pretty much taken from
the Myo C++ headers and translated to Python. The *Quaternion* class
can work with any :class:`Vector` class, as long as it fulfills the
following requirements:

- It's constructor accepts the ``x``, ``y`` and ``z`` components in
  that very order
- Instances have the attributes ``x``, ``y`` and ``z

References
----------

Euler Angles calculation: https://developer.thalmic.com/docs/api_reference/platform/hello-myo_8cpp-example.html
"""

import math
from .vector import Vector


class Quaternion(object):

    __slots__ = ('x', 'y', 'z', 'w')

    def __init__(self, x, y, z, w):
        super(Quaternion, self).__init__()
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = float(w)

    def __mul__(self, rhs):
        """
        Multiplies *self* with the :class:`Quaternion` *rhs* and returns
        a new :class:`Quaternion`.
        """

        if not isinstance(rhs, Quaternion):
            raise TypeError('can only multiply with Quaternion')
        return Quaternion(
            self.w * rhs.x + self.x * rhs.w + self.y * rhs.z - self.z * rhs.y,
            self.w * rhs.y - self.x * rhs.z + self.y * rhs.w + self.z * rhs.x,
            self.w * rhs.z + self.x * rhs.y - self.y * rhs.x + self.z * rhs.w,
            self.w * rhs.w - self.x * rhs.x - self.y * rhs.y - self.z * rhs.z)

    def __iter__(self):
        return iter((self.x, self.y, self.z, self.w))

    def __repr__(self):
        return 'Quaternion({0}, {1}, {2}, {3})'.format(
            self.x, self.y, self.z, self.w)

    def __invert__(self):
        """
        Returns this Quaternion's conjugate.
        """

        return Quaternion(-self.x, -self.y, -self.z, self.w)

    def __getitem__(self, index):
        return (self.x, self.y, self.z, self.w)[index]

    def copy(self):
        """
        Returns a shallow copy of the quaternion.
        """

        return Quaternion(self.x, self.y, self.z, self.w)

    def magnitude(self):
        """
        Returns the magnitude of the quaternion.
        """

        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2 + self.w ** 2)

    def normalized(self):
        """
        Returns the unit quaternion corresponding to the same rotation
        as this one.
        """

        magnitude = self.magnitude()
        return Quaternion(
            self.x / magnitude, self.y / magnitude,
            self.z / magnitude, self.w / magnitude)

    conjugate = __invert__

    def from_axis_angle(self, axis, angle):
        """
        Returns a :class:`Quaternion` that represents the right-handed
        rotation of *angle* radians about the givne *axis*.

        :param axis: The unit vector representing the axis of rotation.
        :param angle: The angle of rotation, in radians.
        """

        sincomp = math.sin(angle / 2.0)
        return Quaternion(
            axis.x * sincomp, axis.y * sincomp,
            axis.z * sincomp, math.cos(angle / 2.0))

    def rotate(self, vec):
        """
        Returns *vec* rotated by this :class:`Quaternion`.

        :param vec: A vector object.
        :return: object of type of *vec*
        """

        qvec = self * Quaternion(vec.x, vec.y, vec.z, 0) * ~self
        return type(vec)(qvec.x, qvec.y, qvec.z)

    @property
    def roll(self):
        """ Calculates the Roll of the Quaternion. """

        return math.atan2(2.0 * (self.w * self.x + self.y * self.z),
                          1.0 - 2.0 * (self.x * self.x + self.y * self.y))

    @property
    def pitch(self):
        """ Calculates the Pitch of the Quaternion. """

        c = 2.0 * (self.w * self.y - self.z * self.x)
        return math.asin(max(-1.0, min(1.0, c)))

    @property
    def yaw(self):
        """ Calculates the Yaw of the Quaternion. """

        return math.atan2(2.0 * (self.w * self.z + self.x * self.y),
                          1.0 - 2.0 * (self.y * self.y + self.z * self.z))

    @property
    def euler(self):
        """ Returns a :class:`Vector` of the euler angles (roll, pitch and yaw). """

        return Vector(self.roll, self.pitch, self.yaw)
    
    rpy = euler

    @staticmethod
    def identity():
        """
        Returns the identity :class:`Quaternion`.
        """

        return Quaternion(0, 0, 0, 1)

    @staticmethod
    def rotation_of(source, dest):
        """
        Returns a :class:`Quaternion` that represents a rotation from
        vector *source* to *dest*.

        :param source: A vector object.
        :param dest: A vector object.
        :return: :class:`Quaternion`
        """

        source = Vector(source.x, source.y, source.z)
        dest = Vector(dest.x, dest.y, dest.z)
        cross = source.cross(dest)
        cos_theta = source.dot(dest)

        # Return identity if the vectors are the same direction.
        if cos_theta >= 1.0:
            return Quaternion.identity()

        # Product of the square of the magnitudes.
        k = math.sqrt(source.dot(source), dest.dot(dest))

        # Return identity in the degenerate case.
        if k <= 0.0:
            return Quaternion.identity()

        # Special handling for vectors facing opposite directions.
        if cos_theta / k <= -1:
            x_axis = Vector(1, 0, 0)
            y_axis = Vector(0, 1, 1)
            if abs(source.dot(x_ais)) < 1.0:
                cross = source.cross(x_axis)
            else:
                cross = source.cross(y_axis)

        return Quaternion(cross.x, cross.y, cross.z, k + cos_theta)
