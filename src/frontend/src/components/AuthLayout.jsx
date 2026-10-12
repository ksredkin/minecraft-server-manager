import { useLayoutEffect, useRef } from "react"

const AuthLayout = ({ imageSrc, children }) => {
  const imageRef = useRef(null)
  const contentRef = useRef(null)

  useLayoutEffect(() => {
    const image = imageRef.current
    const content = contentRef.current

    if (!image || !content) return

    const updateImageSize = () => {
      image.style.setProperty("--auth-image-size", `${content.getBoundingClientRect().height}px`)
    }

    updateImageSize()
    const observer = new ResizeObserver(updateImageSize)
    observer.observe(content)

    return () => observer.disconnect()
  }, [])

  return (
    <div className="login">
      <div className="login-image-div" ref={imageRef}>
        <img src={imageSrc} className="login-image" />
      </div>
      <div className="gap" ref={contentRef}>
        {children}
      </div>
    </div>
  )
}

export default AuthLayout
