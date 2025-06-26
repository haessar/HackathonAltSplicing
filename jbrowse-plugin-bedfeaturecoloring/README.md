# jbrowse-plugin-bedfeaturecoloring
Simple "no-build" ESM plugin for Jbrowse 2, which defines a jexl callback function `colorFeature` to harness the `score` and `itemRgb` columns in a BED file `FeatureTrack` for enhanced visualisation.

`itemRgb` is a string containing a comma-separated list of three integer values representing red, green and blue, each in the range 0-255. e.g. `"255,0,0"` for red.

`score` is an integer value between 0-1000, which is scaled to a float in the range 0-1 for the alpha component of the color.

Each feature line in the BED file will have its color rendered using these two values.

## Quick start
1. Create a local jbrowse-web instance
```
npx @jbrowse/cli create jbrowse-web
cd jbrowse-web
```

2. Launch local instance 
```
npx serve . -p 3000
```

3. Navigate to `http://localhost:3000/?config=https://unpkg.com/@haessar/jbrowse-plugin-bedfeaturecoloring@latest/test_config.json` in browser to use a test `config.json` from the latest version of the plugin.

## Defining custom tracks
The following template `config.json` shows how to define a custom BED `FeatureTrack` to utilise the `colorFeature` function in its display:
```
{
  "plugins": [
    {
      "name": "BedFeatureColoring",
      "esmLoc": { "uri": "https://unpkg.com/@haessar/jbrowse-plugin-bedfeaturecoloring" }
    }
  ],
  "assemblies": [...],
  "tracks": [
    {
      "type": "FeatureTrack",
      "name": "Colored BED Track",
      "adapter": {
        "type": "BedAdapter",
        "bedLocation": { "uri": "path/to/file.bed" }
      },
      "displays": [
        {
          "type": "LinearBasicDisplay",
          "renderer": {
            "type": "SvgFeatureRenderer",
            "color1": "jexl:colorFeature(feature)"
          }
        }
      ]
    }
  ]
}
```

## Contributors

- [@haessar](https://github.com/haessar)
- [@tobyweir](https://github.com/tobyweir)
