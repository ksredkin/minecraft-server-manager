import { useState } from "react"


const PlayersPanel = ({executeCommand, players = [], search, setSearch, apiWorks}) => {
  const filteredPlayers = players.filter(player => player.toLowerCase().includes((search.toLowerCase())))
  const sendCommand = async (command) => {
    if (command) await executeCommand(command)
  }
  const playersItems = filteredPlayers.map((player, index) => {
    return (
      <div className="big-players-card-item" key={index}>
        <img className="big-players-card-item-image" src="steve.png" alt="player" width="35px" height="35px" />
        <h4 className="big-players-card-item-text">{player}</h4>
        <button className={"big-players-card-item-kick-button button-enabled-" + apiWorks} onClick={() => sendCommand("kick " + player)}>Кикнуть</button>
        <button className={"big-players-card-item-ban-button button-enabled-" + apiWorks} onClick={() => sendCommand("ban " + player)}>Бан</button>
      </div>
    )
  })

  return (<div className="panel">
    <div className="big-players-card">
      <div className="big-players-card-header">
        <h3 className="big-players-card-header-text">Игроки</h3>
      </div>

      <div className="big-players-card-subheader">
        <input value={search} onChange={(e) => setSearch(e.target.value)} type="text" className="big-players-card-footer-input" placeholder="🔍︎ Введите ник игрока..."/>
      </div>
            
      <div className="big-players-card-items-div">
        {playersItems}
      </div>
      {(players.length == 0) && <h4 className="big-players-card-no-players-text">Сервер пуст</h4>}
    </div>  
  </div>)
}

export default PlayersPanel
