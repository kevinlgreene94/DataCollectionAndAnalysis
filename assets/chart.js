function createPieChart(data, labels) {
    var ctx = document.getElementById("myPieChart").getContext("2d");
    var existingChart = Chart.getChart(ctx);
    if (existingChart) {
        existingChart.destroy();
    }
    var myPieChart = new Chart(ctx, {
        type: "pie",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Data",
                    data: data,
                    backgroundColor: [
                        "rgba(255, 99, 132, 0.6)",
                        "rgba(54, 162, 235, 0.6)",
                        "rgba(255, 206, 86, 0.6)",
                        "rgba(75, 192, 192, 0.6)",
                        "rgba(153, 102, 255, 0.6)",
                        "rgba(255, 159, 64, 0.6)",
                    ],
                },
            ],
        },
        options: {},
    });
}

function createBarChart(data, labels) {
    var ctx = document.getElementById("myBarChart").getContext("2d");
    var existingChart = Chart.getChart(ctx);
    if (existingChart) {
        existingChart.destroy();
    }
    var myBarChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Number of Employees",
                    data: data,
                    backgroundColor: [
                        "rgba(255, 99, 132, 0.6)",
                        "rgba(54, 162, 235, 0.6)",
                        "rgba(255, 206, 86, 0.6)",
                        "rgba(75, 192, 192, 0.6)",
                        "rgba(153, 102, 255, 0.6)",
                        "rgba(255, 159, 64, 0.6)",
                    ],
                },
            ],
        },
        options: {
            indexAxis: 'y',
        },
    });
}
function createTechChart(data, labels) {
    var ctx = document.getElementById("myTechChart").getContext("2d");
    var existingChart = Chart.getChart(ctx);
    if (existingChart) {
        existingChart.destroy();
    }
    var myTechChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Technologies",
                    data: data,
                    backgroundColor: [
                        "rgba(255, 99, 132, 0.6)",
                        "rgba(54, 162, 235, 0.6)",
                        "rgba(255, 206, 86, 0.6)",
                        "rgba(75, 192, 192, 0.6)",
                        "rgba(153, 102, 255, 0.6)",
                        "rgba(255, 159, 64, 0.6)",
                    ],
                },
            ],
        },
        options: {
        },
    });
}

function getChartData(cmp_size) {
    var endpoint = "/get_piechart_data/";
    if (cmp_size) {
        endpoint += cmp_size;
    }
    fetch(endpoint)
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            var labels = data.labels;
            var chartData = data.chart_data;
            createPieChart(chartData, labels);
        });
}
function getBarChartData(cmp_size) {
    var endpoint = "/get_barchart_data/";
    if (cmp_size) {
        endpoint += cmp_size;
    }
    fetch(endpoint)
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            var labels = data.labels;
            var chartData = data.chart_data;
            createBarChart(chartData, labels);
        });
}
function getTechChartData(cmp_size) {
    var endpoint = "/get_tech_data/";
    if (cmp_size) {
        endpoint += cmp_size;
    }
    fetch(endpoint)
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            var labels = data.labels;
            var chartData = data.chart_data;
            createTechChart(chartData, labels);
        });
}

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("changeCMPSize").addEventListener("click", function () {
        var cmp_size = document.getElementById("cmpSize").value;
        getBarChartData(cmp_size);
        getChartData(cmp_size);
        getTechChartData(cmp_size);
    });
});