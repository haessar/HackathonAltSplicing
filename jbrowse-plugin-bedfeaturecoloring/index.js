//attempts to add colorFeature function to jbrowse

export default class CustomBedPlugin {
    name = 'CustomBedPlugin'

    install() {}
    configure(pluginManager) {
      pluginManager.jexl.addFunction('colorFeature', feature => {
        let score = feature.parentHandle.get('score')
        let colour = feature.parentHandle.get('itemRgb')
        if (score && colour) {
          const alpha = Math.max(0, Math.min(1, score / 100))
          return `rgba(${colour}, ${alpha})`
        }
        return 'red'
      })

    }

  }