PropChart
===

https://github.com/dustractor/propchart

This addon interprets a given input string
as one or more properties of one or more objects
to be displayed for editing in the user interface.

Presets for the input string allow for easy custom
interface to diverse and sundry properties which can
be reached in one of the following ways:

* foo.attribute...
* bar[index]...
* obj["key"]...


Now you can reach properties inside of nodetrees or modifiers.

Display grouping can be changed:

* one list per object
* one list per property
* in a tabular gridlike fashion

[interpolation perhaps should be hidden by default unless specified in preferences.]

Adds an operator which will interpolate the value of a property from the first to the last over all the objects in a selection. It is being implemented on a type by type basis and has so far been implemented where applicability is at least semi obvious.  Int, Float, Vector, Euler Quaternion, Color, etcetera... meaning not all properties are applicable or have been implemented.

The ordering of the objects is based on standard lexical sorting.


