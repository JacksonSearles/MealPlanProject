
function mealplanView() {
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('view', 'mealplan');
    //window.location.href = "{{url_for('mealplan')}}?" + urlParams.toString();
    window.location.href = "/mealplan?" + urlParams.toString();
}

function foodView() {
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('view', 'food');
    // window.location.href = "{{ url_for('food') }}?" + urlParams.toString();
    window.location.href = "/food?" + urlParams.toString();
}

function toggle(){
    const toggleSwitch = document.getElementById('toggleSwitch');
    const graphColumn = document.getElementById('graphColumn')
    const hideableGraph = document.querySelector('.hideable-graph');
    const hideableTable = document.querySelector('.hideable-table');

    // Initial state
    hideableGraph.style.display = toggleSwitch.checked ? 'none' : 'block';
    hideableTable.style.display = toggleSwitch.checked ? 'block' : 'none';

    // Toggle visibility on checkbox change
    toggleSwitch.addEventListener('change', function () {
        if (toggleSwitch.checked) {
            hideableGraph.style.display = 'none';
            hideableTable.style.display = 'flex';
            hideableTable.style.justifyContent = 'center';
            graphColumn.classList.add('is-flex-centered');
        } else {
            hideableGraph.style.display = 'block';
            hideableTable.style.display = 'none';
            hideableTable.style.justifyContent = '';
            graphColumn.classList.remove('is-flex-centered');
        }
    });
}

