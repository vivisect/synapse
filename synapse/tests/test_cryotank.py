import synapse.neuron as s_neuron
import synapse.cryotank as s_cryotank

from synapse.tests.common import *

cryodata = (('foo', {'bar': 10}), ('baz', {'faz': 20}))

class CryoTest(SynTest):

    def test_cryo_tank(self):

        with self.getTestDir() as dirn:

            with s_cryotank.CryoTank(dirn) as tank:

                info = tank.info()
                self.eq(0, info.get('indx'))
                self.eq(0, info.get('metrics'))

                tank.puts(cryodata)
                info = tank.info()
                self.eq(2, info.get('indx'))
                self.eq(1, info.get('metrics'))

                self.eq('baz', tank.last()[1][0])

                retn = tuple(tank.slice(0, 1))
                self.eq(retn, ((0, cryodata[0]),))

                retn = tuple(tank.rows(0, 1))  # coverage related
                self.len(1, retn)
                retn = tuple(tank.rows(0, 2))
                self.len(2, retn)
                data = retn[-1]
                self.eq(data, (1, b'\x92\xa3baz\x81\xa3faz\x14'))

                info = tank.info()
                self.eq(2, info.get('indx'))
                self.eq(1, info.get('metrics'))

                retn = tuple(tank.metrics(0, 1))[0]

                self.nn(retn[1].get('time'))
                self.eq(retn[1].get('size'), 22)
                self.eq(retn[1].get('count'), 2)

                # Slices and rows can start at offsets
                retn = tuple(tank.rows(1, 4))
                self.len(1, retn)
                retn = tuple(tank.slice(1, 4))
                self.len(1, retn)

                retn = tuple(tank.rows(4, 4))
                self.len(0, retn)
                retn = tuple(tank.slice(4, 4))
                self.len(0, retn)

    def test_cryo_cell(self):

        with self.getTestDir() as dirn:

            conf = {'host': '127.0.0.1'}

            with s_cryotank.CryoCell(dirn, conf) as cell:

                port = cell.getCellPort()

                auth = cell.genUserAuth('visi@vertex.link')

                addr = ('127.0.0.1', port)

                user = s_cryotank.CryoUser(auth, addr, timeout=2)

                user._chunksize = 1
                user.puts('woot:woot', cryodata, timeout=2)

                self.eq(user.last('woot:woot', timeout=2)[1][0], 'baz')

                retn = user.list()
                self.eq(retn[0][1]['indx'], 2)
                self.eq(retn[0][0], 'woot:woot')

                metr = user.metrics('woot:woot', 0, 100, timeout=2)

                self.len(2, metr)
                self.eq(metr[0][1]['count'], 1)

                user._chunksize = 1
                user.puts('woot:woot', cryodata, timeout=2)
                retn = list(user.slice('woot:woot', 2, 2))

                self.len(2, retn)
                self.eq(2, retn[0][0])
