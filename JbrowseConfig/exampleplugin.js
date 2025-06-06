//Example from Jbrowse documentation

//This plugin is succesfully added


export default class MyPlugin {
    name = 'MyPlugin'
    version = '1.0'
  
    install(pluginManager) {
      // here, we use jbrequire to reference packages exported through JBrowse
      const { ConfigurationSchema } = pluginManager.jbrequire(
        '@jbrowse/core/configuration',
      )
      const WidgetType = pluginManager.jbrequire(
        '@jbrowse/core/pluggableElementTypes/WidgetType',
      )
      const { ElementId } = pluginManager.jbrequire(
        '@jbrowse/core/util/types/mst',
      )
      const { types } = pluginManager.jbrequire('mobx-state-tree')
  
      const React = pluginManager.jbrequire('react')
  
      // this is our react component
      const CiteWidget = props => {
        // React.createElement can be used to add html to our widget component.
        // We write out raw React.createElement code because JSX requires a build
        // step and can't be used very easily in the no build plugin context
        const header = React.createElement(
          'h1',
          null,
          'Cite this JBrowse session',
        )
        const content = React.createElement(
          'p',
          null,
          `Diesh, Colin, et al. "JBrowse 2: A modular genome browser with views of synteny and structural variation. bioRxiv. 2022.`,
        )
  
        return React.createElement('div', null, [header, content])
      }
  
      // we're adding a widget that we can open upon clicking on our menu item
      pluginManager.addWidgetType(() => {
        // adding a widget to the plugin
        return new WidgetType({
          name: 'CiteWidget',
          heading: 'Cite this JBrowse session',
          configSchema: ConfigurationSchema('CiteWidget', {}),
          stateModel: types.model('CiteWidget', {
            id: ElementId,
            type: types.literal('CiteWidget'),
          }),
          // we're going to provide this component ourselves
          ReactComponent: CiteWidget,
        })
      })
    }
  
    configure(pluginManager) {
      if (pluginManager.rootModel) {
        pluginManager.rootModel.insertMenu('Citations', 4)
  
        pluginManager.rootModel.appendToMenu('Citations', {
          label: 'Cite this JBrowse session',
          onClick: session => {
            // upon clicking on this menu item, we need to add and show our new widget
            const widget = session.addWidget('CiteWidget', 'citeWidget', {
              view: self,
            })
            session.showWidget(widget)
          },
        })
      }
    }
  }