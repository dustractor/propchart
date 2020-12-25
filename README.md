PropChart
===

https://github.com/dustractor/propchart

This addon allows you to:

* access properties not only by dotted attribute access, but also via keyed and indexed access into collections/arrays/lists
* edit the properties of multiple selected objects
* display multiple properties of an object in one location
* display as one list per object, one list per property, or in a tabular grid
* make presets for the properties you need to change or view often
* interpolate the value of a property from the first to the last over all the objects in a selection

Note: only properties which belong to objects can be reached.  Roadmap 2021 includes plans to support datablocks which cannot be selected in the viewport.

Also, interpolation has only been implemented in (hopefully most of the) applicable situations.  Int, Float, Vector, Euler, Color, etcetera... meaning not all properties are applicable or have been implemented.
