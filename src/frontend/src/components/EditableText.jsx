import { useState, useEffect, useRef } from "react"

const EditableText = ({ text, func, currentEditing, setCurrentEditing, id, textClass }) => {
  const [value, setValue] = useState(text)
  const editableTextRef = useRef(null)
  const [correctValue, setCorrectValue] = useState(text)
  const inputRef = useRef(null)

  const executeFunctionAndHide = async () => {
    if (value.length > 0) {
      await func(id, value)
      setCorrectValue(value)
    } else {
      setValue(correctValue)
    }
    setCurrentEditing(null)
  }
  
  const handleKeyDown = async (e) => {
    if (e.key == "Enter") {
      await executeFunctionAndHide()
    }
  }

  const handleMouseDown = async (e) => {
    if (!(editableTextRef.current.contains(e.target)) && (currentEditing == id)) {
      await executeFunctionAndHide()
    }
  }

  useEffect(() => {
    if (!(currentEditing == id)) return
    if (inputRef.current) inputRef.current.focus()

    document.addEventListener("mousedown", handleMouseDown)
    return () => {document.removeEventListener("mousedown", handleMouseDown)}
  }, [currentEditing])

  const show = currentEditing == id

  return (
    <div ref={editableTextRef}>
      {!show && <h3 onClick={() => {setCurrentEditing(id)}} className={textClass}>{value}</h3>}
      {show && <input ref={inputRef} value={value} onChange={(e) => {setValue(e.target.value)}} id={id} className="editable-text-input" type="text" onKeyDown={(e) => {handleKeyDown(e)}} placeholder="Введите новое название сервера..." />}
    </div>
  )
}


export default EditableText
