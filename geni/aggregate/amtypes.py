# Copyright (c) 2014-2017  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import abc

import six

from .core import AMTypeRegistry

class AMType(object):
  __metaclass__ = abc.ABCMeta

  def __init__ (self, name):
    self.name = name

  @abc.abstractmethod
  def parseAdvertisement (self, data):
    return

  @abc.abstractmethod
  def parseManifest (self, data):
    return


class ExoGENI(AMType):
  def __init__ (self, name="exogeni"):
    super(ExoGENI, self).__init__ (name)

  def parseAdvertisement (self, data):
    from ..rspec import pgad
    ad = pgad.Advertisement(xml=data["value"])
    return ad

  def parseManifest (self, data):
    from ..rspec import pgmanifest
    manifest = pgmanifest.Manifest(xml = data["value"])
    return manifest


class ProtoGENI(AMType):
  def __init__ (self, name="pg"):
    super(ProtoGENI, self).__init__(name)

  def parseAdvertisement (self, data):
    from ..rspec import pgad
    ad = pgad.Advertisement(xml=data["value"])
    ad.error_url = data["code"]["protogeni_error_url"]
    return ad

  def parseManifest (self, data):
    from ..rspec import pgmanifest
    if isinstance(data, (six.string_types)):
      manifest = pgmanifest.Manifest(xml = data)
    else:
      manifest = pgmanifest.Manifest(xml = data["value"])
      manifest.error_url = data["code"]["protogeni_error_url"]
    return manifest


class FOAM(AMType):
  def __init__ (self, name="foam"):
    super(FOAM, self).__init__(name)

  def parseAdvertisement (self, data):
    from ..rspec import ofad
    ad = ofad.Advertisement(xml=data["value"])
    return ad

  def parseManifest (self, data):
    from ..rspec import ofmanifest
    manifest = ofmanifest.Manifest(xml = data["value"])
    return manifest


class OpenGENI(AMType):
  def __init__ (self, name="opengeni"):
    super(OpenGENI, self).__init__(name)

  def parseAdvertisement (self, data):
    from ..rspec import pgad
    ad = pgad.Advertisement(xml=data["value"])
    return ad

  def parseManifest (self, data):
    from ..rspec import pgmanifest
    manifest = pgmanifest.Manifest(xml = data["value"])
    return manifest


class VTS(AMType):
  def __init__ (self, name="vts"):
    super(VTS, self).__init__(name)

  def parseAdvertisement (self, data):
    from ..rspec import vtsad
    ad = vtsad.Advertisement(xml=data["value"])
    return ad

  def parseManifest (self, data):
    from ..rspec import vtsmanifest
    if isinstance(data, (six.string_types)):
      manifest = vtsmanifest.Manifest(xml = data)
    else:
      manifest = vtsmanifest.Manifest(xml = data["value"])
    return manifest


class OESS(AMType):
  def __init__ (self, name="oess"):
    super(OESS, self).__init__(name)

  def parseAdvertisement (self, data):
    from ..rspec import oessad
    ad = oessad.Advertisement(xml=data["value"])
    return ad

  def parseManifest (self, data):
    from ..rspec import oessmanifest
    if isinstance(data, (six.string_types)):
      manifest = oessmanifest.Manifest(xml = data)
    else:
      manifest = oessmanifest.Manifest(xml = data["value"])
    return manifest


AMTypeRegistry.register("foam", FOAM())
AMTypeRegistry.register("opengeni", OpenGENI())
AMTypeRegistry.register("pg", ProtoGENI())
AMTypeRegistry.register("exogeni", ExoGENI())
AMTypeRegistry.register("vts", VTS())
AMTypeRegistry.register("oess", OESS())
