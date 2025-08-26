
const sidebarBtn = document.querySelector(".user-profile")
const sidebar = document.querySelector(".sidebar-content")
sidebarBtn.addEventListener("click", ()=>{
    sidebar.classList.add("visible-sidebar")
})

document.querySelector(".close-sidebar").addEventListener("click", ()=>{
    sidebar.classList.remove("visible-sidebar")
})