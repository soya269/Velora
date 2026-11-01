
document.addEventListener("DOMContentLoaded", function () {
    const menuBtn = document.getElementById("menuToggle");
    const sidebar = document.querySelector(".sidebar");
    const main = document.querySelector(".main");

    if (!menuBtn || !sidebar || !main) {
        return;
    }

    menuBtn.addEventListener("click", function () {
        if (window.innerWidth <= 992) {
            // Mobile and tablet
            sidebar.classList.toggle("show");
        } else {
            // Desktop and laptop
            sidebar.classList.toggle("hide");
            main.classList.toggle("expand");
        }
    });

    // Close mobile sidebar when clicking outside
    document.addEventListener("click", function (event) {
        if (
            window.innerWidth <= 992 &&
            sidebar.classList.contains("show") &&
            !sidebar.contains(event.target) &&
            !menuBtn.contains(event.target)
        ) {
            sidebar.classList.remove("show");
        }
    });

    // Reset sidebar when switching between screen sizes
    window.addEventListener("resize", function () {
        if (window.innerWidth > 992) {
            sidebar.classList.remove("show");
        } else {
            sidebar.classList.remove("hide");
            main.classList.remove("expand");
        }
    });
});
