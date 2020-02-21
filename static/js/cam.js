Cookies.set('Admin', false);
var msgs = []
setInterval(refresh_msgs, 2500); //Reload file every 2500 ms or x ms if you wish to c
retrieve_msgs();

function purge_db() {
    if (Cookies.get('Admin') == "true")
    {
        $.ajax({
            type: "GET",
            url: "/purge_db",
            success: function()
            {
                console.log("base de datos limpia")
            },
            error: function(data)
            {
                alert('ERROR\n' + data.responseText);
            },
        });
    } else {
        console.log('no eres admin :(')
    }
    return false;
}

function switch_light() {
    if (Cookies.get('Admin') == "true")
    {
        $('#luz_button').prop("disabled", true);
        $.ajax({
            type: "GET",
            url: "/switch_light",
            success: function(response)
            {
                if (response == "done") {
                    $('#luz_button').prop("disabled", false);
                }
            },
            error: function(data)
            {
                alert('ERROR\n' + data.responseText);
            },
        });
    } else {
        console.log('no eres admin :(')
    }
    return false;
}

function validateUser() {
    var pass = $('#pass-input');
    if (correctPassword(pass.val()) == true) {
        $('#alerta').show();
        $('#admin_panel').show();
        Cookies.set('Admin', true);
        console.log('eres admin! :)');
    } else {
        console.log('no eres admin :(');
        Cookies.set('Admin', false);
        $('#admin_panel').hide();
        $('#alerta').show();
        $('#alerta').html('The provided password is incorrect.');
    }
}

function onSignIn(googleUser) {
    var profile = googleUser.getBasicProfile();
    console.log('ID: ' + profile.getId()); // Do not send to your backend! Use an ID token instead.
    console.log('Name: ' + profile.getName());
    console.log('Image URL: ' + profile.getImageUrl());
    console.log('Email: ' + profile.getEmail()); // This is null if the 'email' scope is not present.
  }

function send_message() {
    var msg = $('#chat_input').val()
    var now = new Date().getTime();
    $.ajax({
        type: "POST",
        url: "/post_message",
        data: JSON.stringify(['user', msg, now]),
        success: function(response)
        {
            console.log(response);
            retrieve_msgs();
            $('#chat_input').val('')
        },
        error: function(data)
        {
            alert('ERROR\n' + data.responseText);
        },
    });
}

function refresh_msgs() {
    // update
    var oldscrollHeight = $("#chatbox").attr("scrollHeight") - 20; //Scroll height before the request
    $("#chatbox").html(msgs); // Insert chat log into the #chatbox div
    //Auto-scroll
    var newscrollHeight = $("#chatbox").attr("scrollHeight") - 20; //Scroll height after the request
    if(newscrollHeight > oldscrollHeight){
        $("#chatbox").animate({ scrollTop: newscrollHeight }, 'normal'); //Autoscroll to bottom of div
    }
}

function retrieve_msgs() {
    $.ajax({
        type: "POST",
        url: "/retrieve_messages",
        data: JSON.stringify([10]), // number of messages to retrieve
        success: function(response)
        {
            /*
            console.log(msgs.length + ' messages retrieved!');
            */
            msgs = JSON.parse(response);
            refresh_msgs();
        },
        error: function(data)
        {
            alert('ERROR\n' + data.responseText);
            console.log(data)
        },
    });
}

function correctPassword(pwd) {
    return pwd == '1234abcd'; // this is horrible
}