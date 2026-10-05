import Header from "../components/Header.jsx"

const Home = () => {
  requestAnimationFrame(() => {
    document.documentElement.classList.add("theme-ready")
  })
  
  return (<div>
    <Header />
  </div>)
}

export default Home