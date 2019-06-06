// fill_dropdown_fetch();
test();


function test() 
{
    console.log("test play.py");
    url = "/play.py";
    const request = new XMLHttpRequest();
    request.open('GET', url, true);
    request.onload = function() {
        if (request.status === 200) {
            console.log("GET data: " + request.responseText);
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


function fill_dropdown() 
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