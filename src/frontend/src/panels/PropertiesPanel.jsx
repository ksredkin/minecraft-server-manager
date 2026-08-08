import { useState, useRef } from "react"
import { ChevronDown } from "lucide-react"

const serverPropertiesSelectOptions = {
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

const PropertiesPanel = ({updateServerProperties, showConfirm, apiWorks, setEditedServerProperties, serverProperties = {}, editedServerProperties = {}}) => {
  const [searchServerProperties, setSearchServerProperties] = useState("")

  const diffKeys = Object.keys(editedServerProperties).filter(key => editedServerProperties[key] !== serverProperties[key])
  const filteredServerProperties = Object.fromEntries(Object.entries(editedServerProperties).filter(([key, value]) => key.toLowerCase().includes(searchServerProperties.toLowerCase())))
  const serverPropertiesCardItems = Object.entries(filteredServerProperties).map(([key, value], index) => {
    const updateProperty = (key, value) => setEditedServerProperties(prev => ({...prev, [key]: value}))
    let element = undefined

    if (serverPropertiesSelectOptions?.[key]) {
      const subElements = serverPropertiesSelectOptions[key].map(option => <option className="settings-card-item-select-option" key={option} value={option}>{option}</option>)
      element = <div className="settings-card-item-select-div"><select className="settings-card-item-select" value={value} onChange={(e) => updateProperty(key, e.target.value)}>{subElements}</select><ChevronDown className="settings-card-item-select-chevron-down"/></div>
    } else {
      if (value === "true" || value === "false") {
        element = <div className={`switch ${value === "true" ? "on" : ""}`} onClick={() => updateProperty(key, value === "true" ? "false" : "true")}>
          <div className={`switch-thumb`}></div>
        </div>
      } else {
        element = <input className="settings-card-item-value" placeholder="Введите значение..." value={value} onChange={(e) => updateProperty(key, e.target.value)}/>
      }
    }

    return <div key={index} className={"settings-card-item settings-card-item-edited-" + diffKeys.includes(key)}>
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
        <input value={searchServerProperties} onChange={(e) => setSearchServerProperties(e.target.value)} type="text" className="server-properties-card-search-input" placeholder="🔍︎ Введите имя настройки..."/>
        <button className={"server-properties-card-subheader-save-button button-enabled-" + (apiWorks && (diffKeys.length > 0))} onClick={() => {showConfirm(async () => {await updateServerProperties()}, "Сохранить изменения?", "Изменённые настройки будут записаны в server.properties.", "Сохранить", "success")}}>{diffKeys.length == 0 ? "Сохранить настройки" : `Сохранить (${diffKeys.length} изменения)`}</button>
        <button className={"server-properties-card-subheader-reset-button button-enabled-" + (apiWorks && (diffKeys.length > 0))} onClick={() => {showConfirm(async () => {setEditedServerProperties(serverProperties)}, "Отменить изменения?", "Все несохранённые изменения будут отменены.", "Отменить", "danger")}}>Отменить изменения</button>
      </div>

      <div className="server-properties-card-items-div">
        {(serverPropertiesCardItems.length == 0) && <h4 className="server-properties-card-items-div-no-items-text">Настроек нет</h4>}
        {serverPropertiesCardItems}
      </div>
    </div>
  </div>)
}

export default PropertiesPanel
