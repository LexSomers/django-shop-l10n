# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.conf import settings

CONTINENTS = (
    ('AF', _('Africa')),
    ('NA', _('North America')),
    ('EU',  _('Europe')),
    ('AS', _('Asia')),
    ('OC',  _('Oceania')),
    ('SA', _('South America')),
    ('AN', _('Antarctica'))
)

AREAS = (
    ('a', _('Another')),
    ('i', _('Island')),
    ('ar', _('Arrondissement')),
    ('at', _('Atoll')),
    ('ai', _('Autonomous island')),
    ('ca', _('Canton')),
    ('cm', _('Commune')),
    ('co', _('County')),
    ('dp', _('Department')),
    ('de', _('Dependency')),
    ('dt', _('District')),
    ('dv', _('Division')),
    ('em', _('Emirate')),
    ('gv', _('Governorate')),
    ('ic', _('Island council')),
    ('ig', _('Island group')),
    ('ir', _('Island region')),
    ('kd', _('Kingdom')),
    ('mu', _('Municipality')),
    ('pa', _('Parish')),
    ('pf', _('Prefecture')),
    ('pr', _('Province')),
    ('rg', _('Region')),
    ('rp', _('Republic')),
    ('sh', _('Sheading')),
    ('st', _('State')),
    ('sd', _('Subdivision')),
    ('sj', _('Subject')),
    ('ty', _('Territory')),
)



class Country(models.Model):
    """
    International Organization for Standardization (ISO) 3166-1 Country list
    """
    iso2_code = models.CharField(_('ISO alpha-2'), max_length=2, unique=True)
    name = models.CharField(_('Official name (CAPS)'), max_length=128)
    printable_name = models.CharField(_('Country name'), max_length=128)
    iso3_code = models.CharField(_('ISO alpha-3'), max_length=3, unique=True)
    numcode = models.PositiveSmallIntegerField(_('ISO numeric'), null=True,
                                               blank=True)
    active = models.BooleanField(_('Country is active'), default=True)
    continent = models.CharField(_('Continent'), choices=CONTINENTS,
                                 max_length=2)
    admin_area = models.CharField(_('Administrative Area'), choices=AREAS,
                                  max_length=2, null=True, blank=True)

    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')
        ordering = ('name',)

    def __unicode__(self):
        return self.printable_name


class AdminArea(models.Model):
    """
    Administrative Area level 1 for a country.  For the US, this would be the
    states
    """
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(_('Admin Area name'), max_length=60, )
    abbrev = models.CharField(_('Postal Abbreviation'), max_length=3,
                              null=True, blank=True)
    active = models.BooleanField(_('Area is active'), default=True)

    class Meta:
        verbose_name = _('Administrative Area')
        verbose_name_plural = _('Administrative Areas')
        ordering = ('name',)

    def __unicode__(self):
        return self.name


BASE_ADDRESS_TEMPLATE = \
_("""
Address: %(address)s,
Zip-Code: %(zipcode)s,
City: %(city)s,
State: %(state)s,
Country: %(country)s,
""")

ADDRESS_TEMPLATE = getattr(settings, 'SHOP_ADDRESS_TEMPLATE',
                           BASE_ADDRESS_TEMPLATE)
class Address(models.Model):
    user_shipping = models.OneToOneField(User, related_name='shipping_address',
                                         blank=True, null=True, on_delete=models.CASCADE)
    user_billing = models.OneToOneField(User, related_name='billing_address',
                                        blank=True, null=True, on_delete=models.CASCADE)

    country = models.ForeignKey(Country, verbose_name=_('country'), on_delete=models.CASCADE)
    state = models.ForeignKey(AdminArea, verbose_name=_('state'), on_delete=models.CASCADE)
    city = models.CharField(_('City'), max_length=20)

    address = models.CharField(_('Address'), max_length=255)
    address2 = models.CharField(_('Address2'), max_length=255, blank=True)
    zip_code = models.CharField(_('Zip Code'), max_length=20)

    class Meta(object):
        abstract = True
        verbose_name = _('Address')
        verbose_name_plural = _("Addresses")

    def __unicode__(self):
        return '%s (%s, %s)' % (self.zip_code, self.city)

    def clone(self):
        new_kwargs = dict([(fld.name, getattr(self, fld.name))
                           for fld in self._meta.fields if fld.name != 'id'])
        return self.__class__.objects.create(**new_kwargs)

    def as_text(self):
        return ADDRESS_TEMPLATE % {
            'address': '%s\n%s' % (self.address, self.address2),
            'zipcode': self.zip_code,
            'city': self.city,
            'state': self.state,
            'country': self.country,
        }
