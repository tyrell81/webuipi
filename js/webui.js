fill_dropdown("pls_list");
volume_manager();   // Get volume value

$("#play_btn").click(function() { play_manager("Play"); }); 
$("#stop_btn").click(function() { play_manager("Stop"); }); 
$("#volume_up").click(function() { volume_manager("Up"); }); 
$("#volume_down").click(function() { volume_manager("Down"); });


function play_manager(command)
{
    dropdown_id = "pls_list";
    let url = "/play.py";    
    const request = new XMLHttpRequest();
    request.open('POST', url, true);
    request.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

    request.onload = function() {
        // 0	UNSENT	Client has been created. open() not called yet.
        // 1	OPENED	open() has been called.
        // 2	HEADERS_RECEIVED	send() has been called, and headers and status are available.
        // 3	LOADING	Downloading; responseText holds partial data.
        // 4	DONE	The operation is complete.
        if (request.status == 200) {
            console.log("Post readyState: " + request.readyState + ", got response: " + request.responseText);
        } else {
            console.log("SEND ERROR, status: " + request.status);
            alert("SEND ERROR, status: " + request.status);
        }
    }
    request.onerror = function() {
        console.error("An error occurred fetching the JSON from " + url);
    };

    let send_data = new FormData();
    if (command.toUpperCase() == "PLAY") {
        let dropdown = document.getElementById(dropdown_id);
        if (dropdown == null) {
            console.log("Dropdown " + dropdown_id + " is null");
            return;
        }
        console.log("dropdown.value: " + dropdown.options[dropdown.selectedIndex].value +
            ", dropdown.text: " + dropdown.options[dropdown.selectedIndex].text);
        let selected_playlist_name = dropdown.options[dropdown.selectedIndex].text;
        if (!selected_playlist_name || selected_playlist_name.trim().length === 0 || selected_playlist_name == "- empty -") {
            console.log("Selected is empty");
            alert("Please select playlist");
            return;
        }

        send_data.append("play", selected_playlist_name);
    }
    if (command.toUpperCase() == "STOP")
        send_data.append("stop", "1");

    send_data_str = new URLSearchParams(send_data).toString();
    console.log("Send: " + send_data_str);
    request.send(send_data_str);
}


function fill_dropdown(dropdown_id)
{
    let dropdown = document.getElementById(dropdown_id);
    if (dropdown == null) {
        console.log("Dropdown " + dropdown_id + " is null");
        return;
    }
    dropdown.length = 0;

    let url = "/play.py";    
    const request = new XMLHttpRequest();
    request.open('GET', url, true);

    request.onload = function() {
        if (request.status == 200) {
            console.log("Get readyState: " + request.readyState + ", got response: " + request.responseText);
            const data = JSON.parse(request.responseText);            
            console.log("data: " + JSON.stringify(data));
            let option;
            for (var i in data) {
                console.log("i: " + i + ", data[i]: " + data[i]);
                option = document.createElement('option');
                option.text = data[i];
                option.value = i;
                dropdown.add(option);
            }
        } else {
            console.log("GET ERROR, status: " + request.status);
            alert("GET ERROR, status: " + request.status);
        }
    }
    request.onerror = function() {
        console.error("An error occurred fetching the JSON from " + url);
    };
    
    console.log("Request GET");
    request.send();
}


function volume_manager(command)
{
    let url = "/play.py";    
    const request = new XMLHttpRequest();    
    request.open('POST', url, true);
    request.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

    request.onload = function() {
        let volume_label = document.getElementById("volume");
        if (volume_label == null) {
            console.log("Volume label " + volume_label + " is null");
            return;
        }
        volume_label.innerHTML = "";
        
        if (request.status == 200) {
            console.log("Post volume readyState: " + request.readyState + ", got response: " + request.responseText);            
            volume_label.innerHTML = request.responseText;// request.responseText
        } else {
            console.log("SEND ERROR, status: " + request.status);
            alert("SEND ERROR, status: " + request.status);
        }
    }
    request.onerror = function() {
        console.error("An error occurred fetching the JSON from " + url);
    };

    let send_data = new FormData();
    if (!command || command.trim().length === 0) {
        send_data.append("volume", "get");
    } else {
        if (command.toUpperCase() == "UP") {
            send_data.append("volume", "up");
        }
        if (command.toUpperCase() == "DOWN") {
            send_data.append("volume", "down");
        }
    }

    send_data_str = new URLSearchParams(send_data).toString();
    console.log("Send: " + send_data_str);
    request.send(send_data_str);
}