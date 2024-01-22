document.onclick = function (event) {
  dropdownButton = document.querySelector('.dropbtn');
  dropdownMenu = document.querySelector(".dropdown-content");
  if ((!dropdownMenu.contains(event.target)) && (!dropdownButton.contains(event.target))){
      dropdownMenu.style.display = 'none';
  }
}

document.addEventListener('DOMContentLoaded', function() {
    const dropdownButton = document.querySelector('.dropbtn');
    const dropdownButtonContent = document.querySelector('.dropbtn-content');
    const dropdownButtonSymbol = document.querySelector('.dropbtn-symbol');
    const dropdownMenu = document.querySelector('.dropdown-content');
    const dropdownMenuOptions = document.querySelectorAll('.dining-hall-option');

    dropdownButton.addEventListener('click', function() {
      dropdownButtonSymbol.innerHTML = (dropdownButtonSymbol.innerHTML == '▼') ? '▲' : '▼';
      dropdownMenu.style.display = (dropdownMenu.style.display === 'block') ? 'none' : 'block';
    });

    dropdownMenuOptions.forEach(function(menuOption) {
      menuOption.addEventListener('click', function() {
        dropdownMenuOptions.forEach(option => option.classList.remove('active'));
        document.querySelectorAll('.food-container').forEach(container => container.style.display = 'none');
        menuOption.classList.add('active');

        const selectedMenuOption = document.getElementById(menuOption.id.replace('-option', '-food-container'));
        selectedMenuOption.style.display = 'block';
        selectedMenuOption.scrollIntoView({ behavior: 'smooth', block: 'start' });
        dropdownMenu.style.display = 'none';
        dropdownButtonContent.textContent = menuOption.textContent;
        dropdownButtonSymbol.innerHTML = '▼';
      });
    });
});

//Updates Open/Closed Status of each food station at dining hall
function updateStatus(containerId){
  const daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const currDate = new Date();
  const currHour = currDate.getHours();
  const currMinute = currDate.getMinutes();
  const currDay = daysOfWeek[currDate.getDay()];

  //Defines a function to take in a time range(Ex: 8:00-10:00), and check if current time is in this range
  const isFoodStationOpen = (timeRange) => {
    const [openingTime, closingTime] = timeRange.split('-');
    const openingHour = parseInt(openingTime.split(':')[0]);
    const openingMinute = parseInt(openingTime.split(':')[1]);
    const closingHour = parseInt(closingTime.split(':')[0]);
    const closingMinute = parseInt(closingTime.split(':')[1]);
    return (currHour > openingHour || (currHour === openingHour && currMinute >= openingMinute)) &&
          (currHour < closingHour || (currHour === closingHour && currMinute < closingMinute));
  };

  const foodStations = document.getElementById(containerId).getElementsByClassName('box');
  for (const foodStation of foodStations) {
    const foodStationHours = foodStation.querySelector('.js-hours').innerText.split(', ').find(stationHours => stationHours.startsWith(currDay));
    //This if statement will be true when food station has two times its open. For example, "11am-1:30pm and 5pm-8pm"
    if (foodStationHours.includes('and')) {
      const [timeRange1, timeRange2] = foodStationHours.split(': ')[1].split(' and ');
      const isOpen = isFoodStationOpen(timeRange1) || isFoodStationOpen(timeRange2);
      foodStation.querySelector('strong').innerText = isOpen ? 'Open' : 'Closed';
      foodStation.querySelector('strong').style.color = isOpen ? '#006747' : 'red';
    } else {
      const timeRange = foodStationHours.split(': ')[1];
      const isOpen = isFoodStationOpen(timeRange);
      foodStation.querySelector('strong').innerText = isOpen ? 'Open' : 'Closed';
      foodStation.querySelector('strong').style.color = isOpen ? '#006747' : 'red';
    }
  }

  for (const foodStation of foodStations) {
    const currentStatusElement = foodStation.querySelector('.current-status');
    const imgElements = foodStation.querySelectorAll('img');
    if (currentStatusElement.textContent.includes('Closed')) {
        for (const imgElement of imgElements) {
            imgElement.style.display = 'none';
        }
    } else if(currentStatusElement.textContent.includes('Open')){
      for (const imgElement of imgElements) {
        imgElement.addEventListener('error', function() {
          imgElement.style.display = 'none';
        });

        if (imgElement.complete && imgElement.naturalWidth === 0) {
            imgElement.style.display = 'none';
        } else {
            imgElement.style.display = 'block';
        }
      }
    }
  }


}




