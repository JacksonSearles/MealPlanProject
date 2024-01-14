document.onclick = function (event) {
    if (!document.getElementById("navbar").contains(event.target)) closemenu();
}

function openmenu() {
    const links = document.getElementById("links");
    links.style.right = "0";
}
function closemenu() {
    const links = document.getElementById("links");
    links.style.right = "-200px";
}

function changeView(view) {
    window.location.href = `/${view}`;
}

function toggle(){
    const toggleSwitch = document.getElementById('toggleSwitch');
    const graphColumn = document.getElementById('graphColumn')
    const graphContainer = document.querySelector('.graph-container')
    const graphContainerTitle = document.querySelector('.daily-spending')
    const hideableGraph = document.querySelector('.hideable-graph');
    const hideableTable = document.querySelector('.hideable-table');

    // Toggle visibility on checkbox change
    toggleSwitch.addEventListener('change', function () {
        if (toggleSwitch.checked) {
            hideableGraph.style.display = 'none';
            hideableTable.style.display = 'block';
            graphColumn.classList.add('is-flex-centered');
            graphContainer.style.minWidth = '200px';
            graphContainerTitle.style.maxWidth = '250px';
        } else {
            document.body.style.zoom = 1;
            location.reload();
        }
    });
}

