include_navigation_html();

function include_navigation_html() {
    var z, i, elmnt, file, xhttp;
    /* Loop through a collection of all HTML elements: */
    z = document.getElementsByTagName("*");
    for (i = 0; i < z.length; i++) {
        elmnt = z[i];
        /*search for elements with a certain atrribute:*/
        file = elmnt.getAttribute("include-navigation-html");
        if (file) {
            /* Make an HTTP request using the attribute value as the file name: */
            xhttp = new XMLHttpRequest();
            xhttp.onreadystatechange = function () {
                if (this.readyState == 4) {
                    if (this.status == 200) {
                        elmnt.innerHTML = this.responseText;
                        var active_page = location.href.split("/").slice(-1);
                        var menu_html_links = elmnt.querySelector("nav div div ul");
                        var menu_html_elements = menu_html_links.getElementsByTagName("a");
                        for (i = 0; i < menu_html_elements.length; i++) {
                            if (menu_html_elements[i].getAttribute("href") == active_page) {
                                menu_html_elements[i].classList.add("active");
                                break;
                            }
                        }
                    }
                    if (this.status == 404) {
                        elmnt.innerHTML = "Page not found.";
                    }
                    /* Remove the attribute, and call this function once more: */
                    elmnt.removeAttribute("include-navigation-html");
                    include_navigation_html();
                }
            };

            xhttp.open("GET", file, true);
            xhttp.send();
            /* Exit the function: */
            return;
        }
    }
}

function login() {
    var username = document.getElementById("Username").value;
    var passwd = document.getElementById("Password").value;
    alert("login: " + username + ":" + passwd);
}

$(function () {
    $("#side-menu").metisMenu();
});

//Loads the correct sidebar on window load,
//collapses the sidebar on window resize.
// Sets the min-height of #page-wrapper to window size
$(function () {
    $(window).bind("load resize", function () {
        topOffset = 50;
        width =
            this.window.innerWidth > 0 ? this.window.innerWidth : this.screen.width;
        if (width < 768) {
            $("div.navbar-collapse").addClass("collapse");
            topOffset = 100; // 2-row-menu
        } else {
            $("div.navbar-collapse").removeClass("collapse");
        }

        height =
            (this.window.innerHeight > 0
                ? this.window.innerHeight
                : this.screen.height) - 1;
        height = height - topOffset;
        if (height < 1) height = 1;
        if (height > topOffset) {
            $("#page-wrapper").css("min-height", height + "px");
        }
    });

    var url = window.location;
    var element = $("ul.nav a")
        .filter(function () {
            return this.href == url || url.href.indexOf(this.href) == 0;
        })
        .addClass("active")
        .parent()
        .parent()
        .addClass("in")
        .parent();
    if (element.is("li")) {
        element.addClass("active");
    }
});
