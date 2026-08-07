import { useRef, useLayoutEffect } from "react"


const TerminalPanel = ({executeCommand, api_works, logs = []}) => {
  const terminal_ref = useRef(undefined)
  const terminal_input_ref = useRef(undefined)
  const should_auto_scroll = useRef(true)

  const handle_terminal_input_key_down = async (event) => {
    if (event.key == "Enter") {
      await executeCommand(terminal_input_ref.current.value)
      terminal_input_ref.current.value = ""
    }
  }

  const handle_terminal_send_button = async () => {
    await executeCommand(terminal_input_ref.current.value)
    terminal_input_ref.current.value = ""
  }

  const onTerminalScroll = () => {
    const container = terminal_ref.current
    should_auto_scroll.current = container.scrollHeight - container.scrollTop - container.clientHeight < 80
  }
  
  useLayoutEffect(() => {
    if (!should_auto_scroll.current) return
    const container = terminal_ref.current
    container.scrollTop = container.scrollHeight
  }, [logs])

  const logs_rows = logs.map((log, index) => {return <h5 key={index} className="log-row">{log}</h5>})

  return (<div className="panel">
    <div className="big-logs-card">
      <div className="logs-card-header">
        <h3 className="logs-card-header-text">Консоль</h3>
      </div>
              
      <div className="big-logs-background" ref={terminal_ref}>
        {logs_rows}
      </div>

      <div className="logs-card-footer">
        <input className="logs-card-input" type="text" placeholder="Введите команду..." ref={terminal_input_ref} onKeyDown={handle_terminal_input_key_down} onScroll={onTerminalScroll} />
        <button className={"logs-card-send-button button-enabled-" + api_works} onClick={handle_terminal_send_button}>Отправить</button>
      </div>
    </div>
  </div>)
}

export default TerminalPanel
