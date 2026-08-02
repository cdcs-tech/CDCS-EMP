/*
====================================================
Dashboard JavaScript
====================================================
*/

document.addEventListener("DOMContentLoaded", () => {

    const chart = document.getElementById("performanceChart");

    if (!chart) {

        return;

    }

    new Chart(chart, {

        type: "bar",

        data: {

            labels: [
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun"
            ],

            datasets: [

                {

                    label: "Sample Data",

                    data: [
                        12,
                        19,
                        8,
                        15,
                        22,
                        18
                    ]

                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false

        }

    });

});
