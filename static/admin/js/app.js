const menuBtn = document.getElementById("menuToggle");

menuBtn.addEventListener("click", function () {

    document.querySelector(".sidebar").classList.toggle("hide");

    document.querySelector(".main").classList.toggle("expand");

});