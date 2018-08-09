import synapse.exc as s_exc
import synapse.common as s_common

import synapse.tests.common as s_test


class TelcoModelTest(s_test.SynTest):
    def test_telco_simple(self):
        with self.getTestCore() as core:

            typ = core.model.type('tel:mob:mcc')
            self.eq(typ.norm('001')[0], '001')
            self.raises(s_exc.BadTypeValu, typ.norm, '01')
            self.raises(s_exc.BadTypeValu, typ.norm, '0001')

            typ = core.model.type('tel:mob:mnc')
            self.eq(typ.norm('01')[0], '01')
            self.eq(typ.norm('001')[0], '001')
            self.raises(s_exc.BadTypeValu, typ.norm, '0001')
            self.raises(s_exc.BadTypeValu, typ.norm, '1')

            with core.snap() as snap:
                # tel:mob:tac
                oguid = s_common.guid()
                props = {'manu': 'Acme Corp',
                         'model': 'eYephone 9000',
                         'internal': 'spYphone 9000',
                         'org': oguid,
                         }
                node = snap.addNode('tel:mob:tac', 1, props)
                self.eq(node.ndef[1], 1)
                self.eq(node.get('manu'), 'acme corp')
                self.eq(node.get('model'), 'eyephone 9000')
                self.eq(node.get('internal'), 'spyphone 9000')
                self.eq(node.get('org'), oguid)
                # defvals
                node = snap.addNode('tel:mob:tac', 2)
                self.eq(node.get('manu'), '??')
                self.eq(node.get('model'), '??')
                self.eq(node.get('internal'), '??')

                # tel:mob:imid
                node = snap.addNode('tel:mob:imid', (490154203237518, 310150123456789))
                self.eq(node.ndef[1], (490154203237518, 310150123456789))
                self.eq(node.get('imei'), 490154203237518)
                self.eq(node.get('imsi'), 310150123456789)

                # tel:mob:imsiphone
                node = snap.addNode('tel:mob:imsiphone', (310150123456789, '+7(495) 124-59-83'))
                self.eq(node.ndef[1], (310150123456789, '74951245983'))
                self.eq(node.get('imsi'), 310150123456789)
                self.eq(node.get('phone'), '74951245983')

                # tel:mob:mcc
                node = snap.addNode('tel:mob:mcc', '666')
                self.eq(node.ndef[1], '666')

                # tel:mob:carrier
                node = snap.addNode('tel:mob:carrier', ('001', '02'), {'org': oguid, 'loc': 'us'})
                self.eq(node.ndef[1], ('001', '02'))
                self.eq(node.get('mcc'), '001')
                self.eq(node.get('mnc'), '02')
                self.eq(node.get('org'), oguid)
                self.eq(node.get('loc'), 'us')

                # tel:mob:cell
                node = snap.addNode('tel:mob:cell', (('001', '02'), 3, 4), {'radio': 'Pirate  ',
                                                                            'latlong': (0, 0)})
                self.eq(node.get('carrier'), ('001', '02'))
                self.eq(node.get('carrier:mcc'), '001')
                self.eq(node.get('carrier:mnc'), '02')
                self.eq(node.get('lac'), 3)
                self.eq(node.get('cid'), 4)
                self.eq(node.get('radio'), 'pirate')
                self.eq(node.get('latlong'), (0.0, 0.0))

    def test_telco_imei(self):
        with self.getTestCore() as core:
            with core.snap() as snap:
                # proper value
                node = snap.addNode('tel:mob:imei', '490154203237518')
                self.eq(node.ndef[1], 490154203237518)
                self.eq(node.get('serial'), 323751)
                self.eq(node.get('tac'), 49015420)
                # One without the check bit (it gets added)
                node = snap.addNode('tel:mob:imei', '39015420323751')
                self.eq(node.ndef[1], 390154203237519)
                # Invalid checksum
                self.raises(s_exc.BadPropValu, snap.addNode, 'tel:mob:imei', 490154203237519)
                self.raises(s_exc.BadPropValu, snap.addNode, 'tel:mob:imei', '20')
                self.raises(s_exc.BadPropValu, snap.addNode, 'tel:mob:imei', 'hehe')

    def test_telco_imsi(self):
        with self.getTestCore() as core:
            with core.snap() as snap:
                node = snap.addNode('tel:mob:imsi', '310150123456789')
                self.eq(node.ndef[1], 310150123456789)
                self.eq(node.get('mcc'), '310')
                self.raises(s_exc.BadPropValu, snap.addNode, 'tel:mob:imsi', 'hehe')
                self.raises(s_exc.BadPropValu, snap.addNode, 'tel:mob:imsi', 1111111111111111)

    def test_telco_phone(self):
        with self.getTestCore() as core:
            t = core.model.type('tel:phone')
            norm, subs = t.norm('123 456 7890')
            self.eq(norm, '1234567890')
            self.eq(subs, {'subs': {'loc': 'us'}})

            norm, subs = t.norm('123 456 \udcfe7890')
            self.eq(norm, '1234567890')

            norm, subs = t.norm(1234567890)
            self.eq(norm, '1234567890')
            self.eq(subs, {'subs': {'loc': 'us'}})

            norm, subs = t.norm('+1911')
            self.eq(norm, '1911')
            self.eq(subs, {'subs': {'loc': 'us'}})

            self.eq(t.repr('12345678901'), '+1 (234) 567-8901')
            self.eq(t.repr('9999999999'), '+9999999999')

            self.raises(s_exc.BadTypeValu, t.norm, -1)
            self.raises(s_exc.BadTypeValu, t.norm, '+()*')

            with core.snap() as snap:
                node = snap.addNode('tel:phone', '+1 (703) 555-1212')
                self.eq(node.ndef[1], '17035551212')
                self.eq(node.get('loc'), 'us')
                node = snap.addNode('tel:phone', '+1 (703) 555-2424')
                # Esnap search
                nodes = list(snap.getNodesBy('tel:phone', 17035552424))
                self.len(1, nodes)
                self.eq(nodes[0].ndef[1], '17035552424')
                # Prefix search
                nodes = list(snap.getNodesBy('tel:phone', '1703555*'))
                self.len(2, nodes)
