// Make sure we wait to attach our handlers until the DOM is fully loaded.
$(document).ready(function() {

  $('.sidenav').sidenav();
  // $('.chips').chips();
  // $('.chips-placeholder').chips({
  //   placeholder: 'Enter a username',
  //   secondaryPlaceholder: '+Interest',
  // });

  // var chip = {
  //   tag: 'chip content',
  //   image: '', //optional
  // };
  // var elem = $('.chips')
  // var instance = M.Chips.getInstance(elem);
  // instance.selectChip(2); // Select 2nd chip

  var modalelems = document.querySelectorAll('.modal');
  var modalinstances = M.Modal.init(modalelems, {});

  var dateelems = document.querySelectorAll('.datepicker');
  var dateinstances = M.Datepicker.init(dateelems, {format: "mm/dd/yyyy"});

  var timeelems = document.querySelectorAll('.timepicker');
  var timeinstances = M.Timepicker.init(timeelems, {});

  $("#radiobtn").click(function(){
    var radioValue = $("input[name='group1']:checked").val();
    if(radioValue){
        alert("Your chose " + radioValue);
    }
  });
  $("#addSchedule-button").click(function(){
    $(".datechoices").append('<div class="input-field col s4">' +
                                                  '<input type="text" class="datepicker">' +
                                                  '<label for="postText">Date</label>' +
                                                '</div>' +
                                                '<div class="input-field col s4">' +
                                                  '<input type="text" class="timepicker">' +
                                                  '<label for="postText">From Time</label>' +
                                                '</div>' +
                                                '<div class="input-field col s4">' +
                                                  '<input type="text" class="timepicker">' +
                                                  '<label for="postText">To Time</label>' +
                                                '</div>')
  });

  function getData() {
    $.ajax({
        url: "/test1",
        method: "GET"
    }).then(function(response) {
        console.log("GET root worked fine\n",response);
        $("#test1").append("<p style='font-weight: bold'> Type: " + response.tasks[0].description + "</p><br>");
    });
  };
  getData();

  $(document.body).on("click", "#test2btn", function(event) {
    event.preventDefault();
    var text = $("#test2txt").val().trim()
    $("#reg-form").append("<p style='font-weight: bold'> Typed: " + text + "</p><br>")
    console.log("text value:", text)

    var msg = {
      textmsg: text 
    }

    $.post("/test2", msg)
    .then(function(data) {
      console.log("got data back from POST call", data.textmsg);
      alert("POST worked...");
    });

  });

});