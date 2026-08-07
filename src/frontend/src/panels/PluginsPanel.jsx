import { useState, useRef } from "react"
import { Package, Trash } from "lucide-react"
import { installPlugin } from "../api/plugins"


const PluginsPanel = ({setSearchInstalledPlugins, plugins, search_installed_plugins, api_works, deletePlugin, searchPlugins, installPlugin}) => {
  const [search_plugins_input_value, setSearchPluginsInputValue] = useState("")
  const [searched_plugins, setSearchedPlugins] = useState([])
  const [installing_plugins, setInstallingPlugins] = useState([])
  const search_plugins_timer = useRef(undefined)

  const create_smart_search_plugins_timer = async (plugin) => {
    if (search_plugins_timer.current) clearTimeout(search_plugins_timer.current)
    if (plugin == "") return setSearchedPlugins([])

    search_plugins_timer.current = setTimeout(async () => {
      try {
        const result = await searchPlugins(plugin)
        setSearchedPlugins(result.data.plugins)
      } catch {
        setSearchedPlugins([])
      }
    }, 1000)
  }

  const handle_install_plugin = async (slug) => {
    setInstallingPlugins(prev => [...prev, slug])
    try {
      await installPlugin(slug)
    } finally {
      setInstallingPlugins(prev => prev.filter(plugin => plugin !== slug))
    }
  }

  const get_install_plugin_button_or_status = (plugin) => {
    if (plugins.includes(plugin.slug)) return <h4 className="big-plugins-card-subcard-items-div-item-downloaded-text">Установлен</h4>
    if (installing_plugins.includes(plugin.slug)) return <h4 className="big-plugins-card-subcard-items-div-item-downloaded-text">Устанавливается...</h4>
    return <button className={"big-plugins-card-subcard-items-div-item-download-button button-enabled-" + (api_works)} onClick={() => handle_install_plugin(plugin.slug)}>Установить</button>
  }

  const searched_plugins_items = searched_plugins.map((plugin, index) => {
    return <div key={index} className="big-plugins-card-subcard-items-div-item">
      <img className="big-plugins-card-subcard-items-div-item-image" src={plugin.icon_url}/>
      <h3>{plugin.title}</h3>
      <h4>{plugin.description}</h4>
      <div className="big-plugins-card-subcard-items-div-item-version-downloads-download-div">
        <h4 style={{marginTop: "5px"}}>{plugin.downloads} загрузок</h4>
        {get_install_plugin_button_or_status(plugin)}
      </div>
    </div>
  })

  const filtered_installed_plugins = plugins.filter(plugin => plugin.toLowerCase().includes((search_installed_plugins.toLowerCase())))
  const installed_plugins_items = filtered_installed_plugins.map((plugin, index) => {
    return (
      <div className="left-big-plugins-card-subcard-items-div-item" key={index}>
        <Package className="big-plugins-card-subcard-items-div-package-image"/>
        <h4 className="big-plugins-card-subcard-items-div-item-text">{plugin[0].toUpperCase() + plugin.slice(1)}</h4>
        <button className={"big-plugins-card-subcard-items-div-item-delete-button button-enabled-" + api_works} onClick={() => deletePlugin(plugin)}><Trash className="big-plugins-card-subcard-items-div-item-delete-button-trash-image"/></button>
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
            <input value={search_installed_plugins} onChange={(e) => setSearchInstalledPlugins(e.target.value)} type="text" className="big-plugins-card-subcard-footer-input" placeholder="🔍︎ Введите имя плагина..."/>
          </div>

          <div className="left-big-plugins-card-subcard-items-div">
            {installed_plugins_items}
            {(plugins.length == 0) && <h4 className="big-plugins-card-subcard-no-plugins-text">Плагинов нет</h4>}
          </div>
        </div>

        <div className="big-plugins-card-subcard">
          <div className="big-plugins-card-subcard-header">
            <h3 className="big-plugins-card-subcard-header-text">Найти и установить</h3>
          </div>

          <div className="big-plugins-card-subcard-header">
            <input value={search_plugins_input_value} onChange={(e) => {setSearchPluginsInputValue(e.target.value); create_smart_search_plugins_timer(e.target.value)}} type="text" className="big-plugins-card-subcard-footer-input" placeholder="🔍︎ Введите имя плагина..."/>
          </div>

          <div className="big-plugins-card-subcard-items-div">
            {searched_plugins_items}
            {(searched_plugins_items.length == 0) && <h4 className="big-plugins-card-subcard-no-plugins-text">Плагинов нет</h4>}
          </div>
        </div>
      </div>
    </div>
  </div>)
}

export default PluginsPanel
