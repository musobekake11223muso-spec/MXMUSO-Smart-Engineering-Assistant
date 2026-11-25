document.addEventListener("DOMContentLoaded", () => {
    const links = document.querySelectorAll("nav a");

    links.forEach(link => {
        link.addEventListener("click", event => {
            const target = link.getAttribute("href");

            if (target && target.startsWith("#")) {
                event.preventDefault();

                const section = document.querySelector(target);

                links.forEach(item => item.classList.remove("active"));
                link.classList.add("active");

                if (section) {
                    section.scrollIntoView({
                        behavior: "smooth",
                        block: "center"
                    });
                } else {
                    alert("Bu modul hali ishlab chiqilmoqda!");
                }
            }
        });
    });

    console.log("Navigatsiya tizimi tayyor!");
});
