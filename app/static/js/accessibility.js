/*
====================================================
Accessibility
====================================================
*/

document.addEventListener("DOMContentLoaded", () => {

    document
        .querySelectorAll("button, a")
        .forEach(element => {

            element.addEventListener("keyup", event => {

                if (event.key === "Enter") {

                    element.click();

                }

            });

        });

});
