=====
Slots
=====

Slots is a simplistic key-value store that leverages the Tapis metadata
API to write and retrieve data using a known, but random, identifying key.

Create a new Slot
Hand off the name to another, future session
Write to the slot
Read from the slot in yet another future session

Same-session create and write
------------------------------

Initialize a ``Slot`` client and create a new slot. Verify that the slot is
available from reading using the ``ready()`` method. Write a value to the slot,
check its status/readiness, then read out the new value.

>>> p = Slot(agave=ag).create()
'slot-tacbobot-WdyXERrroKml3'
>>> p.ready()
False
>>> p.write('this is the value')
>>> p.ready()
True
>>> p.status()
'READY'
>>> p.read()
'this is the value'


Deferred write
--------------

Create the Slot using a Tapis client instance. Find the Slot's name using
``Slot.name``. Determine whether the Slot has been written to via
``Slot.status()`` or ``Slot.ready()``. Initialize a second Slot client. Write
to the previously created Slot by its key name. Verify that it is now ready for
reading.

>>> q = Slot(agave=ag).create()
'slot-vaughn-EjG48L2GWjlX6'
>>> q.name
'slot-vaughn-EjG48L2GWjlX6'
>>> q.status()
'CREATED'
>>> q.ready()
False
>>> r = Slot(agave=ag)
>>> r.write('this is the value', key_name='slot-vaughn-EjG48L2GWjlX6')
>>> r.ready('slot-vaughn-EjG48L2GWjlX6')
True
>>> q.read('slot-vaughn-EjG48L2GWjlX6')
'this is the value'

Initialize a client and write in another session
>>> q = Slot(agave=ag)
>>> q.write('a very nice value', key_name='slot-vaughn-EjG48L2GWjlX6')

Check the status
>>> q.status('slot-vaughn-EjG48L2GWjlX6')
'READY'

# In another client session, check if the slot has been written
ag = Agave.restore()
p = slot(agave=ag)
p.status('slot-tacbobot-WdyXERrroKml3')

# In another client session, write a value to the named slot
ag = Agave.restore()
p = Slot(agave=ag)
p.write('value goes here', key_name='slot-tacbobot-WdyXERrroKml3')

