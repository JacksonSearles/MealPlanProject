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
    const dropdownContent = document.querySelector('.dropdown-content');
    const options = document.querySelectorAll('.dining-hall-option');

    dropdownButton.addEventListener('click', function() {
      dropdownContent.style.display = (dropdownContent.style.display === 'block') ? 'none' : 'block';
      dropdownButtonSymbol.innerHTML = (dropdownButtonSymbol.innerHTML == '▼') ? '▲' : '▼';
    });

    options.forEach(function(option) {
      option.addEventListener('click', function() {
        dropdownButtonContent.textContent = option.textContent;
        options.forEach(function(opt) {
          opt.classList.remove('active');
        });
        option.classList.add('active');
        dropdownContent.style.display = 'none';
        dropdownButtonSymbol.innerHTML = '▼';

        document.querySelectorAll('.food-container').forEach(function(container) {
          container.style.display = 'none';
        });

        const selectedOptionId = option.id.replace('-option', '-food-container');
        document.getElementById(selectedOptionId).style.display = 'block';
      });
    });
    //updateStatus('c4-food-container');
});

//Updates Open/Closed Status on each food station at dining hall
function updateStatus(containerId) {
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
}



