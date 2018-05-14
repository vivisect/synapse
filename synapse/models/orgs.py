from synapse.common import guid

import synapse.lib.module as s_module


class OuModule(s_module.CoreModule):
    def getModelDefs(self):
        modl = {
            'types': (
                ('ou:sic', ('str', {'regex': r'^[0-9]{4}$'}), {
                    'doc': 'The four digit Standard Industrial Classification Code.',
                    'ex': '0111',
                }),
                ('ou:naics', ('str', {'regex': r'^[1-9][0-9]{4}[0-9]?$'}), {
                    'doc': 'The five or six digit North American Industry Classification System code.',
                    'ex': '541715',
                }),
                ('ou:org', ('guid', {}), {
                    'doc': 'A GUID for a human organization such as a company or military unit',
                }),
                ('ou:alias', ('str', {'lower': True, 'regex': r'^[0-9a-z]+$'}), {
                    'doc': 'An alias for the org GUID',
                    'ex': 'vertexproject',
                }),
                ('ou:hasalias', ('comp', {'fields': (('org', 'ou:org'), ('alias', 'ou:alias'))}), {
                    'doc': 'The knowledge that an organization has an alias.',
                }),
                ('ou:name', ('str', {'lower': True, 'strip': True}), {
                    'doc': 'The formal name of an organization',
                    'ex': 'acme corporation',
                }),
                ('ou:member', ('comp', {'fields': (('org', 'ou:org'), ('person', 'ps:person'))}), {
                    'doc': 'A person who is (or was) a member of an organization.',
                }),
                ('ou:suborg', ('comp', {'fields': (('org', 'ou:org'), ('sub', 'ou:org'))}), {
                    'doc': 'Any parent/child relationship between two orgs. May represent ownership, organizational structure, etc.',
                }),
                ('ou:org:has', ('comp', {'fields': (('org', 'ou:org'), ('node', 'ndef'))}), {
                    'doc': 'An org owns, controls, or has exclusive use of an object or resource, '
                           'potentially during a specific period of time.',
                }),
                ('ou:user', ('comp', {'fields': (('org', 'ou:org'), ('user', 'inet:user'))}), {
                    'doc': 'A user name within an organization',
                }),
                ('ou:meet', ('guid', {}), {
                    'doc': 'A informal meeting of people which has no title or sponsor.  See also: ou:conference.',
                }),
                ('ou:meet:attendee', ('comp', {'fields': (('meet', 'ou:meet'), ('person', 'ps:person'))}), {
                    'doc': 'Represents a person attending a meeting represented by an ou:meet node.',
                }),
                ('ou:conference', ('guid', {}), {
                    'doc': 'A conference with a name and sponsoring org.',
                }),
                ('ou:conference:attendee', ('comp', {'fields': (('conference', 'ou:conference'), ('person', 'ps:person'))}), {
                    'doc': 'Represents a person attending a conference represented by an ou:conference node.',
                }),
            ),
            'forms': (
                ('ou:org', {}, (
                    ('loc', ('loc', {}), {
                        'doc': 'Location for an organization.'
                    }),
                    ('name', ('ou:name', {}), {
                        'doc': 'The localized name of an organization.',
                    }),
                    ('name:en', ('ou:name', {}), {
                        'doc': 'The English name of an organization.',
                    }),
                    ('alias', ('ou:alias', {}), {
                        'doc': 'The default alias for an organization'
                    }),
                    ('phone', ('tel:phone', {}), {
                        'doc': 'The primary phone number for the organization.',
                    }),
                    ('sic', ('ou:sic', {}), {
                        'doc': 'The Standard Industrial Classification code for the organization.',
                    }),
                    ('naics', ('ou:naics', {}), {
                        'doc': 'The North American Industry Classification System code for the organization.',
                    }),
                    ('us:cage', ('gov:us:cage', {}), {
                        'doc': 'The Commercial and Government Entity (CAGE) code for the organization.',
                    }),
                    ('url', ('inet:url', {}), {
                        'doc': 'The primary url for the organization.',
                    }),
                )),
                ('ou:hasalias', {}, (
                    ('org', ('ou:org', {}), {
                        'ro': True,
                        'doc': 'Org guid',
                    }),
                    ('alias', ('ou:alias', {}), {
                        'ro': True,
                        'doc': 'Alias for the organization',
                    }),
                    # FIXME Add seen:min and seen:max
                )),
                ('ou:member', {}, (
                    ('org', ('ou:org', {}), {
                        'ro': True,
                        'doc': 'The GUID of the org the person is a member of.',
                    }),
                    ('person', ('ps:person', {}), {
                        'ro': True,
                        'doc': 'The GUID of the person that is a member of an org.',
                    }),
                    ('title', ('str', {'lower': True, 'strip': True}), {
                        'doc': 'The persons normalized title.'
                    }),
                    ('start', ('time', {'ismin': True}), {
                        'doc': 'Earliest known association of the person with the org.',
                    }),
                    ('end', ('time', {'ismax': True}), {
                        'doc': 'Most recent known association of the person with the org.',
                    })
                )),
                ('ou:suborg', {}, (
                    ('org', ('ou:org', {}), {
                        'ro': True,
                        'doc': 'The org which owns the sub organization',
                    }),
                    ('sub', ('ou:org', {}), {
                        'ro': True,
                        'doc': 'The sub org which owned by the org.',
                    }),
                    ('perc', ('int', {'min': 0, 'max': 100}), {
                        'doc': 'The optional percentage of sub which is owned by org',
                    }),
                    ('current', ('bool', {}), {
                        'doc': 'Bool indicating if the suborg relationship still current.',
                    }),
                    # FIXME Add seen:min and seen:max to indicate beginning
                    # and end dates of the suborg relationship
                )),
                ('ou:org:has', {}, (
                    ('org', ('ou:org', {}), {
                        'ro': True,
                        'doc': 'The org who owns or controls the object or resource.',
                    }),
                    ('node', ('ndef', {}), {
                        'ro': True,
                        'doc': 'The object or resource that is owned or controlled by the org.',
                    }),
                    ('node:form', ('str', {}), {
                        'ro': True,
                        'doc': 'The form of the object or resource that is owned or controlled by the org.',
                    }),
                    # FIXME Add seen:min and seen:max
                    # ('seen:min', {'ptype': 'time:min',
                    #               'doc': 'The earliest known time when the org owned or controlled the resource.'}),
                    # ('seen:max', {'ptype': 'time:max',
                    #               'doc': 'The most recent known time when the org owned or controlled the resource.'}),
                )),
                ('ou:user', {}, (
                    ('org', ('ou:org', {}), {
                        'ro': True,
                        'doc': 'Org guid',
                    }),
                    ('user', ('inet:user', {}), {
                        'ro': True,
                        'doc': 'The username associated with the organization',
                    }),
                )),
                ('ou:meet', {}, (
                    ('name', ('str', {'lower': True}), {
                        'doc': 'A human friendly name for the meeting.',
                    }),
                    ('start', ('time', {}), {
                        'doc': 'The date / time the meet starts.',
                    }),
                    ('end', ('time', {}), {
                        'doc': 'The date / time the meet ends.',
                    }),
                    # FIXME Needs geospatial model
                    # ('place', ('geo:place', ()), {
                    #     'doc': 'The geo:place node where the meet was held.',
                    # }),
                )),
                ('ou:meet:attendee', {}, (
                    ('meet', ('ou:meet', {}), {
                        'ro': True,
                        'doc': 'The meeting which was attended.',
                    }),
                    ('person', ('ps:person', {}), {
                        'ro': True,
                        'doc': 'The person who attended the meeting.',
                    }),
                    ('arrived', ('time', {}), {
                        'doc': 'The time when a person arrived to the meeting.',
                    }),
                    ('departed', ('time', {}), {
                        'doc': 'The time when a person departed from the meeting.',
                    }),
                )),
                ('ou:conference', {}, (
                    ('org', ('ou:org', {}), {
                        'doc': 'The org which created/managed the conference.',
                    }),
                    ('name', ('str', {'lower': True, 'req': True}), {
                        'doc': 'The full name of the conference.',
                        'ex': 'decfon 2017',
                    }),
                    ('base', ('str', {'lower': True, 'strip': True}), {
                        'doc': 'The base name which is shared by all conference instances.',
                        'ex': 'defcon',
                    }),
                    ('start', ('time', {}), {
                        'doc': 'The conference start date / time.',
                    }),
                    ('end', ('time', {}), {
                        'doc': 'The conference end date / time.',
                    }),
                    # FIXME Needs geospatial model
                    # ('place', ('geo:place', ()), {
                    #     'doc': 'The geo:place node where the conference was held.',
                    # }),
                    # TODO: prefix optimized geo political location
                )),
                ('ou:conference:attendee', {}, (
                    ('conference', ('ou:conference', {}), {
                        'ro': True,
                        'doc': 'The conference which was attended.',
                    }),
                    ('person', ('ps:person', {}), {
                        'ro': True,
                        'doc': 'The person who attended the conference.',
                    }),
                    ('arrived', ('time', {}), {
                        'doc': 'The time when a person arrived to the conference.',
                    }),
                    ('departed', ('time', {}), {
                        'doc': 'The time when a person departed from the conference.',
                    }),
                    ('role:staff', ('bool', {}), {
                        'doc': 'The person worked as staff at the conference.',
                    }),
                    ('role:speaker', ('bool', {}), {
                        'doc': 'The person was a speaker or presenter at the conference.',
                    }),
                 )),
            )
        }

        name = 'ou'
        return ((name, modl),)

# FIXME: What do we want to do with seedCtors?
class Fixme:

    def initCoreModule(self):
        self.core.addSeedCtor('ou:org:name', self.seedOrgName)
        self.core.addSeedCtor('ou:org:alias', self.seedOrgAlias)

    def seedOrgName(self, prop, valu, **props):
        node = self.core.getTufoByProp('ou:org:name', valu)
        if node is None:
            node = self.core.formTufoByProp('ou:org', guid(), name=valu, **props)
        return node

    def seedOrgAlias(self, prop, valu, **props):
        node = self.core.getTufoByProp('ou:org:alias', valu)
        if node is None:
            node = self.core.formTufoByProp('ou:org', guid(), alias=valu, **props)
        return node
