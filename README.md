# French Polygonesia

Parse polygons the French government wants blurred.

A French law requires certain areas to be blurred in published imagery. There is a schedule of all the polygons that this applies to [here](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000048234967). (Please note that although it relates tangentially to secrets, this is public, unclassified information, available on the open web.) This repo contains code to parse that page into geoJSON.

This is the first working draft; it shouldn’t be relied upon for actual legal compliance or any other important purpose. Its only intent to is visualize the data for general interest.

## Limitations

As of this commit, these are the known bugs:

- There’s no testing to notice if polygons (or individual points) are missed.
- Everything is packed into one giant MultiPolygon, which is clearly semantically wrong.
- Floats are printed at full precision, which is obviously overkill and makes the output much longer than it needs to be.
- Metadata (such as site names) is not copied into the polygons.

## Contributing

Please clone this repo and improve it as you see fit. This is a 90 minute project that I do not intend to polish or maintain.
