import AdapterType from '@jbrowse/core/pluggableElementTypes/AdapterType'

import configSchema from './configSchema'

import type PluginManager from '@jbrowse/core/PluginManager'

export default function BedAdapterF(pluginManager: PluginManager) {
  pluginManager.addAdapterType(
    () =>
      new AdapterType({
        name: 'BedAdapter2',
        displayName: 'BED adapter 2',
        configSchema,
        getAdapterClass: () => import('./BedAdapter2').then(r => r.default),
      }),
  )
}
