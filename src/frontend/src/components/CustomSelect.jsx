
import { useEffect, useRef, useState } from "react"
import { ChevronDown } from "lucide-react"

export default function CustomSelect({
  options,
  value,
  onChange,
  placeholder = "Выберите значение",
  disabled = false,
  className = "",
}) {
  const [isOpen, setIsOpen] = useState(false)
  const [isMenuScrollable, setIsMenuScrollable] = useState(false)
  const selectRef = useRef(null)

  const selectedOption = options.find(
    (option) => option.value === value
  )

  useEffect(() => {
    function handleClickOutside(event) {
      if (
        selectRef.current &&
        !selectRef.current.contains(event.target)
      ) {
        setIsOpen(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)

    return () => {
      document.removeEventListener(
        "mousedown",
        handleClickOutside
      )
    }
  }, [])

  useEffect(() => {
    if (!isOpen) return

    function handleKeyDown(event) {
      if (event.key === "Escape") {
        setIsOpen(false)
      }
    }

    document.addEventListener("keydown", handleKeyDown)

    return () => {
      document.removeEventListener("keydown", handleKeyDown)
    }
  }, [isOpen])

  function handleSelect(option) {
    onChange(option.value)
    setIsOpen(false)
  }

  function handleMenuTransitionEnd(event) {
    if (
      event.target === event.currentTarget &&
      event.propertyName === "grid-template-rows"
    ) {
      setIsMenuScrollable(isOpen)
    }
  }

  return (
    <div
      className={`custom-select ${className}`.trim()}
      ref={selectRef}
    >
      <button
        type="button"
        className={`custom-select__trigger ${
          isOpen ? "is-open" : ""
        }`}
        onClick={() => {
          if (!isOpen) setIsMenuScrollable(false)
          setIsOpen((prev) => !prev)
        }}
        disabled={disabled}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <span
          className={
            selectedOption
              ? "custom-select__value"
              : "custom-select__placeholder"
          }
        >
          {selectedOption?.label ?? placeholder}
        </span>

        <ChevronDown
          size={18}
          className="custom-select__icon"
        />
      </button>

      <div
        className={`custom-select__menu ${isOpen ? "is-open" : ""} ${
          isMenuScrollable ? "is-scrollable" : ""
        }`}
        role="listbox"
        aria-hidden={!isOpen}
        onTransitionEnd={handleMenuTransitionEnd}
      >
        <div className="custom-select__menu-content">
          {options.map((option) => (
            <button
              key={option.value}
              type="button"
              role="option"
              aria-selected={option.value === value}
              className={`custom-select__option ${
                option.value === value ? "is-selected" : ""
              }`}
              onClick={() => handleSelect(option)}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
