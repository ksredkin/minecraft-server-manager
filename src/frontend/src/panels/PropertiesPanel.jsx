import { useState, useRef } from "react"
import { ChevronDown } from "lucide-react"

const server_properties_select_options = {
    difficulty: [
        "peaceful",
        "easy",
        "normal",
        "hard"
    ],

    gamemode: [
        "survival",
        "creative",
        "adventure",
        "spectator"
    ],

    "level-type": [
        "minecraft:normal",
        "minecraft:flat",
        "minecraft:large_biomes",
        "minecraft:amplified"
    ]
  }

const PropertiesPanel = ({update_server_properties, ask_confirmation, api_works, setEditedServerProperties, server_properties = {}, edited_server_properties = {}}) => {
  const [search_server_properties, setSearchServerProperties] = useState("")

  const diff_keys = Object.keys(edited_server_properties).filter(key => edited_server_properties[key] !== server_properties[key])
  const filtered_server_properties = Object.fromEntries(Object.entries(edited_server_properties).filter(([key, value]) => key.toLowerCase().includes(search_server_properties.toLowerCase())))
  const server_properties_card_items = Object.entries(filtered_server_properties).map(([key, value], index) => {
    const updateProperty = (key, value) => setEditedServerProperties(prev => ({...prev, [key]: value}))
    let element = undefined

    if (server_properties_select_options?.[key]) {
      const sub_elements = server_properties_select_options[key].map(option => <option className="settings-card-item-select-option" key={option} value={option}>{option}</option>)
      element = <div className="settings-card-item-select-div"><select className="settings-card-item-select" value={value} onChange={(e) => updateProperty(key, e.target.value)}>{sub_elements}</select><ChevronDown className="settings-card-item-select-chevron-down"/></div>
    } else {
      if (value === "true" || value === "false") {
        element = <div className={`switch ${value === "true" ? "on" : ""}`} onClick={() => updateProperty(key, value === "true" ? "false" : "true")}>
          <div className={`switch-thumb`}></div>
        </div>
      } else {
        element = <input className="settings-card-item-value" placeholder="Введите значение..." value={value} onChange={(e) => updateProperty(key, e.target.value)}/>
      }
    }

    return <div key={index} className={"settings-card-item settings-card-item-edited-" + diff_keys.includes(key)}>
      <h4 className="settings-card-item-name">{key}</h4>
      {element}
    </div>
  })

  return (<div className="panel">
    <div className="server-properties-card">
      <div className="server-properties-card-header">
        <h3 className="server-properties-card-header-text">Настройки</h3>
      </div>

      <div className="server-properties-card-subheader">
        <input value={search_server_properties} onChange={(e) => setSearchServerProperties(e.target.value)} type="text" className="server-properties-card-search-input" placeholder="🔍︎ Введите имя настройки..."/>
        <button className={"server-properties-card-subheader-save-button button-enabled-" + api_works} onClick={() => {ask_confirmation(async () => {await update_server_properties()}, "Сохранить изменения?", "Изменённые настройки будут записаны в server.properties.", "Сохранить", "success")}}>{diff_keys.length == 0 ? "Сохранить настройки" : `Сохранить (${diff_keys.length} изменения)`}</button>
        <button className="server-properties-card-subheader-reset-button" onClick={() => {ask_confirmation(async () => {setEditedServerProperties(server_properties)}, "Отменить изменения?", "Все несохранённые изменения будут отменены.", "Отменить", "danger")}}>Отменить изменения</button>
      </div>

      <div className="server-properties-card-items-div">
        {(server_properties_card_items.length == 0) && <h4 className="server-properties-card-items-div-no-items-text">Настроек нет</h4>}
        {server_properties_card_items}
      </div>
    </div>
  </div>)
}

export default PropertiesPanel
