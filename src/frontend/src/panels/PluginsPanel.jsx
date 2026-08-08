import { useState, useRef } from "react"
import { Package, Trash } from "lucide-react"
import { installPlugin } from "../api/plugins"


const PluginsPanel = ({setSearchInstalledPlugins, plugins, searchInstalledPlugins, apiWorks, deletePlugin, searchPlugins, installPlugin}) => {
  const [searchPluginsInputValue, setSearchPluginsInputValue] = useState("")
  const [searchedPlugins, setSearchedPlugins] = useState([])
  const [installingPlugins, setInstallingPlugins] = useState([])
  const searchPluginsTimer = useRef(undefined)

  const createSmartSearchPluginsTimer = async (plugin) => {
    if (searchPluginsTimer.current) clearTimeout(searchPluginsTimer.current)
    if (plugin == "") return setSearchedPlugins([])

    searchPluginsTimer.current = setTimeout(async () => {
      try {
        const result = await searchPlugins(plugin)
        setSearchedPlugins(result.data.plugins)
      } catch {
        setSearchedPlugins([])
      }
    }, 1000)
  }

  const handleInstallPlugin = async (slug) => {
    setInstallingPlugins(prev => [...prev, slug])
    try {
      await installPlugin(slug)
    } finally {
      setInstallingPlugins(prev => prev.filter(plugin => plugin !== slug))
    }
  }

  const getInstallPluginButtonOrStatus = (plugin) => {
    if (plugins.includes(plugin.slug)) return <h4 className="big-plugins-card-subcard-items-div-item-downloaded-text">Установлен</h4>
    if (installingPlugins.includes(plugin.slug)) return <h4 className="big-plugins-card-subcard-items-div-item-downloaded-text">Устанавливается...</h4>
    return <button className={"big-plugins-card-subcard-items-div-item-download-button button-enabled-" + apiWorks} onClick={() => handleInstallPlugin(plugin.slug)}>Установить</button>
  }

  const searchedPluginsItems = searchedPlugins.map((plugin, index) => {
    return <div key={index} className="big-plugins-card-subcard-items-div-item">
      <img className="big-plugins-card-subcard-items-div-item-image" src={plugin.icon_url}/>
      <h3>{plugin.title}</h3>
      <h4>{plugin.description}</h4>
      <div className="big-plugins-card-subcard-items-div-item-version-downloads-download-div">
        <h4 style={{marginTop: "5px"}}>{plugin.downloads} загрузок</h4>
        {getInstallPluginButtonOrStatus(plugin)}
      </div>
    </div>
  })

  const filteredInstalledPlugins = plugins.filter(plugin => plugin.toLowerCase().includes((searchInstalledPlugins.toLowerCase())))
  const installedPluginsItems = filteredInstalledPlugins.map((plugin, index) => {
    return (
      <div className="left-big-plugins-card-subcard-items-div-item" key={index}>
        <Package className="big-plugins-card-subcard-items-div-package-image"/>
        <h4 className="big-plugins-card-subcard-items-div-item-text">{plugin[0].toUpperCase() + plugin.slice(1)}</h4>
        <button className={"big-plugins-card-subcard-items-div-item-delete-button button-enabled-" + apiWorks} onClick={() => deletePlugin(plugin)}><Trash className="big-plugins-card-subcard-items-div-item-delete-button-trash-image"/></button>
      </div>
    )
  })

  return (<div className="panel">
    <div className="big-plugins-card">
      <h2>Плагины</h2>
      <div className="big-plugins-card-subcards-div">
        <div className="big-plugins-card-subcard">
          <div className="big-plugins-card-subcard-header">
            <h3 className="big-plugins-card-subcard-header-text">Установленные</h3>
          </div>

          <div className="big-plugins-card-subcard-header">
            <input value={searchInstalledPlugins} onChange={(e) => setSearchInstalledPlugins(e.target.value)} type="text" className="big-plugins-card-subcard-footer-input" placeholder="🔍︎ Введите имя плагина..."/>
          </div>

          <div className="left-big-plugins-card-subcard-items-div">
            {installedPluginsItems}
            {(plugins.length == 0) && <h4 className="big-plugins-card-subcard-no-plugins-text">Плагинов нет</h4>}
          </div>
        </div>

        <div className="big-plugins-card-subcard">
          <div className="big-plugins-card-subcard-header">
            <h3 className="big-plugins-card-subcard-header-text">Найти и установить</h3>
          </div>

          <div className="big-plugins-card-subcard-header">
            <input value={searchPluginsInputValue} onChange={(e) => {setSearchPluginsInputValue(e.target.value); createSmartSearchPluginsTimer(e.target.value)}} type="text" className="big-plugins-card-subcard-footer-input" placeholder="🔍︎ Введите имя плагина..."/>
          </div>

          <div className="big-plugins-card-subcard-items-div">
            {searchedPluginsItems}
            {(searchedPluginsItems.length == 0) && <h4 className="big-plugins-card-subcard-no-plugins-text">Плагинов нет</h4>}
          </div>
        </div>
      </div>
    </div>
  </div>)
}

export default PluginsPanel
