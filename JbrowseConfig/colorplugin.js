//attempts to add colorFeature function to jbrowse

//function is never called, unsure why


export default class CustomBedPlugin {
    name = 'CustomBedPlugin'
    version = '0.0.1'
    install() {}
    configure(pluginManager) {
      pluginManager.jexl.addFunction('colorFeature', feature => {
        let score= feature.get('score')
        let colour= feature.get('itemRgb')
        if (score && colour) {
          return 'rgba(${colour}, ${score})'
        }
        return 'red'
      })
      
    }

  }