function showSearch(){
    document.getElementById("navbarSearchContainer").classList.remove("hidden");
    document.getElementById("navbarSearchContainer").classList.add("make-active");
}
function hideSearch(){
    document.getElementById("navbarSearchContainer").classList.remove("make-active");
    document.getElementById("navbarSearchContainer").classList.add("hidden");
}

(
    function(){
        document.getElementById("navbarSearchTogglerOpen").addEventListener("click", showSearch);
        document.getElementById("navbarSearchTogglerClose").addEventListener("click", hideSearch);
    }
)();