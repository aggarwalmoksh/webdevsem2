$(document).ready(function() {
    var eventsPerPage = 4;
    var currentPage = 1;
    var eventsData = [];  // To store the fetched events

    // Fetch events when the page loads
    fetchEvents($('#location').val());

    // Handle location change and fetch new events
    $('#location').change(function() {
        currentPage = 1;  // Reset to first page
        fetchEvents($(this).val());
    });

    // Function to fetch events
    function fetchEvents(location) {
        $.get('/get_events', { location: location }, function(events) {
            eventsData = events;
            displayEvents();
        });
    }

    // Function to display events
    function displayEvents() {
        // Calculate start and end indices for the current page
        var startIndex = (currentPage - 1) * eventsPerPage;
        var endIndex = startIndex + eventsPerPage;
        var eventsToDisplay = eventsData.slice(startIndex, endIndex);

        // Clear previous events
        $('#events-container').empty();

        // Display events
        if (eventsToDisplay.length > 0) {
            eventsToDisplay.forEach(function(event) {
                var eventHtml = '<div class="event">' +
                                    '<img src="static/images/' + event.image + '" alt="' + event.name + '" />' +
                                    '<div class="event-name">' + event.name + '</div>' +
                                  '</div>';
                $('#events-container').append(eventHtml);
            });
        } else {
            $('#events-container').html('<p>No events found for this location.</p>');
        }

        // Update pagination button visibility
        $('#prev-btn').prop('disabled', currentPage === 1);
        $('#next-btn').prop('disabled', currentPage * eventsPerPage >= eventsData.length);
    }

    // Handle Next button click
    $('#next-btn').click(function() {
        if (currentPage * eventsPerPage < eventsData.length) {
            currentPage++;
            displayEvents();
        }
    });

    // Handle Previous button click
    $('#prev-btn').click(function() {
        if (currentPage > 1) {
            currentPage--;
            displayEvents();
        }
    });
});