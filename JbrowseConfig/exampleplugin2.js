//This is an alternative colorFeature function from the Jbrowse documentation

//This is also never called unsure why, Issue seems to be in config.json



export default class MyPlugin {
    name = 'MyPlugin'
    version = '1.0.0'
    install() {}
    configure(pluginManager) {
      pluginManager.jexl.addFunction('colorFeature', feature => {
        let type = feature.get('type')
        if (type === 'CDS') {
          return 'red'
        } else if (type === 'exon') {
          return 'green'
        } else {
          return 'purple'
        }
      })
    }
  }