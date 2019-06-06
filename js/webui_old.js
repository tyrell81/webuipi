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


function play_manager_jq(command)
{
    let post_data = {};
    if (command.toUpperCase() == "PLAY") {
        console.log("Send stop before play");
        post_data = {};
        post_data["stop"] = "1";
        $.post(url, post_data, function(result) {
            console.log("post ok, result: " + result);
            console.log("Send PLAY");
            post_data = {};
            post_data["play"] = "1";
            $.post(url, post_data, function(result) {
                console.log("post ok, result: " + result);
            });
        });        
    }
    if (command.toUpperCase() == "STOP") {
        console.log("Send STOP");
        post_data["stop"] = "1";
        $.post(url, post_data, function(result) {
            console.log("post ok, result: " + result);
        });
    }    
}

function test() 
{
    console.log("test play.py");
    url = "/play.py";
    const request = new XMLHttpRequest();
    request.open('GET', url, true);
    request.onload = function() {
        if (request.status === 200) {
            console.log("GET data: " + request.responseText);
            alert("GET data: " + request.responseText);
            const data = JSON.parse(request.responseText);
            console.log("GET Json data: " + data);
        } else {
            console.log("GET ERROR");
        }
    }
    request.onerror = function() {
        console.error('An error occurred fetching the JSON from ' + url);
    };
    request.send();

    $(function(){
        let post_data = {};
        post_data["test"] = "test from javascript";
        $.post(url, post_data, function(result) {
            console.log("post ok");
            console.log("result: " + result);
        });
        console.log("111111");
    });
}


function fill_dropdown_old() 
{
    dropdown_id = "pls_list";
    url = "/play.py?list";
    default_text = "Select playlist";

    let dropdown = document.getElementById(dropdown_id);
    dropdown.length = 0;

    const request = new XMLHttpRequest();
    request.open('GET', url, true);

    request.onload = function() {
        if (request.status === 200) {
            const data = JSON.parse(request.responseText);
            let option;
            if (data.length == 0) {
                console.log(data.length == 0);
                let defaultOption = document.createElement("option");
                defaultOption.text = " - empty - ";
                dropdown.add(defaultOption);
                dropdown.selectedIndex = 0;
            }
            console.log("data.length:" + data.length);
            for (let i = 0; i < data.length; i++) {
                option = document.createElement('option');
                option.text = data[i].name;
                option.value = data[i].abbreviation;
                dropdown.add(option);
            }
        } else {
            // Reached the server, but it returned an error
            let defaultOption = document.createElement("option");
            defaultOption.text = " - server error - ";
            dropdown.add(defaultOption);
            dropdown.selectedIndex = 0;
        }   
    }

    request.onerror = function() {
        console.error('An error occurred fetching the JSON from ' + url);
    };

    request.send();
}

function fill_dropdown_fetch()
{
    dropdown_id = "pls_list";
    url = "/play.py";
    default_text = "Select playlist";

    let dropdown = document.getElementById(dropdown_id);
    dropdown.length = 0;

    fetch(url)  
        .then(  
        function(response) {  
            if (response.status !== 200) {  
            console.warn('Looks like there was a problem. Status Code: ' + 
                response.status);  
            return;  
            }
    
            // Examine the text in the response  
            response.json().then(function(data) {  
            let option;
            console.log("data: " + JSON.stringify(data));
            for (let i = 0; i < data.length; i++) {
                option = document.createElement('option');
                option.text = data[i].name;
                option.value = data[i].abbreviation;
                dropdown.add(option);
            }    
            });  
        }  
        )  
        .catch(function(err) {  
        console.error('Fetch Error -', err);  
        });        
}