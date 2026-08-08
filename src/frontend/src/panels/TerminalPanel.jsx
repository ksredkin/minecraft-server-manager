import { useRef, useLayoutEffect } from "react"


const TerminalPanel = ({executeCommand, apiWorks, logs = []}) => {
  const terminalRef = useRef(undefined)
  const terminalInputRef = useRef(undefined)
  const shouldAutoScroll = useRef(true)

  const handleTerminalInputKeyDown = async (event) => {
    if (event.key == "Enter") {
      await executeCommand(terminalInputRef.current.value)
      terminalInputRef.current.value = ""
    }
  }

  const handleTerminalSendButton = async () => {
    await executeCommand(terminalInputRef.current.value)
    terminalInputRef.current.value = ""
  }

  const onTerminalScroll = () => {
    const container = terminalRef.current
    shouldAutoScroll.current = container.scrollHeight - container.scrollTop - container.clientHeight < 80
  }
  
  useLayoutEffect(() => {
    if (!shouldAutoScroll.current) return
    const container = terminalRef.current
    container.scrollTop = container.scrollHeight
  }, [logs])

  const logsRows = logs.map((log, index) => {return <h5 key={index} className="log-row">{log}</h5>})

  return (<div className="panel">
    <div className="big-logs-card">
      <div className="logs-card-header">
        <h3 className="logs-card-header-text">Консоль</h3>
      </div>
              
      <div className="big-logs-background" ref={terminalRef} onScroll={onTerminalScroll}>
        {logsRows}
      </div>

      <div className="logs-card-footer">
        <input className="logs-card-input" type="text" placeholder="Введите команду..." ref={terminalInputRef} onKeyDown={handleTerminalInputKeyDown} />
        <button className={"logs-card-send-button button-enabled-" + apiWorks} onClick={handleTerminalSendButton}>Отправить</button>
      </div>
    </div>
  </div>)
}

export default TerminalPanel
