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
    updateStatus('c4-food-container');
});


//Updates Open/Closed Status on each food station at dining hall
function updateStatus(containerId) {
  const daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const currDate = new Date();
  const currHour = currDate.getHours();
  const currMinute = currDate.getMinutes();
  const currDay = daysOfWeek[currDate.getDay()];

  const foodStations = document.getElementById(containerId).getElementsByClassName('box');
  for (i = 0; i < foodStations.length; i++) {
    const foodStation = foodStations[i];
    const foodStationHours = foodStation.querySelector('.js-hours').innerText.split(', ');
    const currDaySchedule = foodStationHours.find(dayHours => dayHours.startsWith(currDay));
    //This if statement will be true when a food station has two times they are open. For example, "11pm-1:30pm and 5pm-8pm"
    if(currDaySchedule.includes('and')){
      const [timeRange1, timeRange2] = currDaySchedule.split(': ')[1].split(' and ');
      const [openingTime1, closingTime1] = timeRange1.split('-');
      const [openingTime2, closingTime2] = timeRange2.split('-');
      const openingHour1 = parseInt(openingTime1.split(':')[0]);
      const openingMinute1 = parseInt(openingTime1.split(':')[1]);
      const closingHour1 = parseInt(closingTime1.split(':')[0]);
      const closingMinute1 = parseInt(closingTime1.split(':')[1]);
      const openingHour2 = parseInt(openingTime2.split(':')[0]);
      const openingMinute2 = parseInt(openingTime2.split(':')[1]);
      const closingHour2 = parseInt(closingTime2.split(':')[0]);
      const closingMinute2 = parseInt(closingTime2.split(':')[1]);
      //Checks if the current time is in between the opening and closing hour of each time slot of the food station
      if (((currHour > openingHour1 || (currHour == openingHour1 && currMinute >= openingMinute1)) && (currHour < closingHour1 || (currHour == closingHour1 && currMinute < closingMinute1)))
      || ((currHour > openingHour2 || (currHour == openingHour2 && currMinute >= openingMinute2)) && (currHour < closingHour2|| (currHour == closingHour2 && currMinute < closingMinute2)))) {
        foodStation.querySelector('strong').innerText = 'Open';
        foodStation.querySelector('strong').style.color = '#006747';
      } else {
        foodStation.querySelector('strong').innerText = 'Closed';
        foodStation.querySelector('strong').style.color = 'red';
      }
    } else {
      const [openingTime, closingTime] = currDaySchedule.split(': ')[1].split('-');
      const openingHour = parseInt(openingTime.split(':')[0]);
      const openingMinute = parseInt(openingTime.split(':')[1]);
      const closingHour = parseInt(closingTime.split(':')[0]);
      const closingMinute = parseInt(closingTime.split(':')[1]);
      //Checks if the current time is in between the opening and closing hour of the food station
      if ((currHour > openingHour || (currHour == openingHour && currMinute >= openingMinute)) 
      && (currHour < closingHour || (currHour == closingHour && currMinute < closingMinute))) {
        foodStation.querySelector('strong').innerText = 'Open';
        foodStation.querySelector('strong').style.color = '#006747';
      } else {
        foodStation.querySelector('strong').innerText = 'Closed';
        foodStation.querySelector('strong').style.color = 'red';
      }
    }
  } 
}


