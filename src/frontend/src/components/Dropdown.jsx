import { useState, useLayoutEffect, useEffect, useRef } from "react"

const Dropdown = ({trigger, options, addtitionalGap = 0}) => {
  const [showMenu, setShowMenu] = useState(false)
  const triggerButtonRef = useRef(null)
  const menuRef = useRef(null)

  useEffect(() => {
    const clickListener = (event) => {
      const target = event.target
      if (
        showMenu &&
        target instanceof Node &&
        !triggerButtonRef.current?.contains(target) &&
        !menuRef.current?.contains(target)
      ) {
        setShowMenu(false)
      }
    }
  
    document.addEventListener("mousedown", clickListener)
    return () => {
      document.removeEventListener("mousedown", clickListener)
    }
  }, [showMenu])

  const [menuStyles, setMenuStyles] = useState({})

  useLayoutEffect(() => {
    if (!showMenu) return

    const menu = menuRef.current
    const trigger = triggerButtonRef.current

    if (!menu || !trigger) return

    const menuRect = menu.getBoundingClientRect()
    const triggerRect = trigger.getBoundingClientRect()

    const spaceBelow = window.innerHeight - triggerRect.bottom
    const spaceAbove = triggerRect.top

    const showBottom =
      spaceBelow >= menuRect.height + 10 + addtitionalGap ||
      spaceBelow >= spaceAbove

    const showLeft =
      triggerRect.right - menuRect.width >= 0

    const styles = {
      ...(showBottom
        ? { top: `${triggerRect.height + 10 + addtitionalGap}px` }
        : { bottom: `${triggerRect.height + 10 + addtitionalGap}px` }),

      ...(showLeft
        ? { right: "0px" }
        : { left: "0px" }),
    }

    setMenuStyles(styles)
  }, [showMenu, addtitionalGap])

  const handleButtonClick = (action) => {
    action()
    setShowMenu(false)
  }

  const buttons = options.map((option, index) => {
    const IconComponent = option.icon
    return <button key={index} onClick={() => handleButtonClick(option.action)} className={"menu-button " + (option?.styles ? option.styles : "")}><IconComponent size={20} />{option.text}</button>
  })

  return (<div className="dropdown">
    <button className="trigger-button" onClick={() => {setShowMenu(prev => !prev)}} ref={triggerButtonRef}>
      {trigger}
    </button>
    <div hidden={!showMenu} className="menu" ref={menuRef} style={menuStyles}>
      <div className="menu-buttons">
        {...buttons}
      </div>
    </div>
  </div>)
}


export default Dropdown
