// Make sure we wait to attach our handlers until the DOM is fully loaded.

// We will handle SU priviledges here

$(document).ready(function() {

  $('.sidenav').sidenav();
  $('.tabs').tabs();
  
  // $('.chips').chips();
  // $('.chips-placeholder').chips({
  //   placeholder: 'Enter a username',
  //   secondaryPlaceholder: '+User',
  // });
  // let chipElem = $(".chips")
  // var chipInstance = M.Chips.getInstance(chipElem);

  var modalElems = document.querySelectorAll('.modal');
  var modalInstances = M.Modal.init(modalElems, {});

  var selectElems = document.querySelectorAll('select');
  var selectInstances = M.FormSelect.init(selectElems, {});

  var selectInstance = M.FormSelect.getInstance(selectElems);

  let email = localStorage.getItem('email');
  console.log("email logged in:\t", email);

  $("#userEmail").text(email);

  $.ajax({
    url: "/getAllUserEmails",
    method: "GET"
  }).then(function(response) {
      console.log("GOT BACK SOMETHING")
      console.log("NOW: \n", response.allUsersEmail.length);
      console.log("Data:\n",response["allUsersEmail"])

      for(let i = 0; i< response.allUsersEmail.length; i++){
        console.log(response["allUsersEmail"][i])
        if(response["allUsersEmail"][i] != email){
          $('#whiteEmailAddition').append(`<option value="${response["allUsersEmail"][i]}"> 
                                              ${response["allUsersEmail"][i]} 
                                           </option>`); 
          $('#blackEmailAddition').append(`<option value="${response["allUsersEmail"][i]}"> 
                                              ${response["allUsersEmail"][i]} 
                                            </option>`);                         
        }
          
      }
      $('select').formSelect();
      
  });

  $(document.body).on("click", "#addWhite-button", function(event) {

    console.log("EMAIL ADDITION: \t", $('#whiteEmailAddition').val())
    let addWhiteData = {
      userEmail: email,
      emailAddition: $('#whiteEmailAddition').val()
    }

    $.post("/addToWhiteBox", JSON.stringify(addWhiteData))
    .then(function(response) {
      console.log("ADD TO WHITEBOX call worked with\t " + JSON.stringify(response));
      M.toast({html: response["Message"]})
    });
  })

  $(document.body).on("click", "#addBlack-button", function(event) {

    console.log("BLACK EMAIL ADDITION: \t", $('#blackEmailAddition').val())
    let addBlackData = {
      userEmail: email,
      emailAddition: $('#blackEmailAddition').val()
    }

    $.post("/addToBlackBox", JSON.stringify(addBlackData))
    .then(function(response) {
      console.log("ADD TO BLACKBOX call worked with\t " + JSON.stringify(response));
      M.toast({html: response["Message"]})
    });
  })


    emailData = {
      email: email
    }
    $.post("/getUserData", JSON.stringify(emailData))
    .then(function(response) {
      // console.log("call worked with\t " + JSON.stringify(response));
      $("#userEmail").text(response["userData"][1]);
      $("#reputationScore").text(response["userData"][4]);
    });


  $(document.body).on("click", "#createGroup-button", function(event) {
    event.preventDefault();


    let groupName = $("#groupName").val().trim()

    createGroupData = {
      groupName: groupName,
      email: email
    }

    // console.log(JSON.stringify(createGroupData))

    $.post("/createGroup", JSON.stringify(createGroupData))
    .then(function(response) {
      // console.log("call worked with\t " + JSON.stringify(response));
    });

    location.reload();

  });


  $.post("/getUserData", JSON.stringify(emailData))
  .then(function(response) {
    console.log("GROUUPS::::\t " + JSON.stringify(response["userData"][3]));

    for(let i=0; i<response["userData"][3].length; i++){

      console.log("LOOOPING in GetUserData")
      let groupName = response["userData"][3][i]

      groupNameJSON = {
        groupName: groupName
      }

      $.post("/getGroupData", JSON.stringify(groupNameJSON))
      .then(function(response) {
        console.log("GroupData ACTIVE AND CLOSED\t " + JSON.stringify(response));
        console.log("GroupData ACTIVE AND CLOSED\t " + JSON.stringify(response["groupData"][1]));

        if((response["groupData"][1]) == "ACTIVE"){

          $("#groupsDiv").append('<div class="col s12 m4">' +
                                  `<div class="card blue-grey darken-1">` +
                                    `<div class="card-content white-text">` +
                                      `<span class="card-title">${response["groupData"][0]}</span>` +
                                    `</div>` +
                                    `<div class="card-action">` +
                                      `<a href="/groupMainPage" target=”_blank”>View</a>` +
                                    `</div>` +
                                  `</div>` +
                                `</div>`)
        }
      });
    }

    // GERENATE WHITE LIST
    for(let i=0; i<response["userData"][8].length; i++){

      // console.log("LOOOPING in GetUserData for WhiteList", response["userData"][8][i])
      $("#whiteListDiv").append('<div class="col s4 m2">' +
                              `<div class="card blue-grey darken-1">` +
                                `<div class="card-content white-text"> User Email: `  +
                                  `<span class="card-title">${response["userData"][8][i]}</span>` +
                                `</div>` +
                              `</div>` +
                            `</div>`)

    }

    // GENERATE BLACK LIST
    for(let i=0; i<response["userData"][7].length; i++){

      console.log("LOOOPING in GetUserData for BLACK LIST", response["userData"][7][i])
      $("#blackListDiv").append('<div class="col s4 m2">' +
                              `<div class="card blue-grey darken-1">` +
                                `<div class="card-content white-text"> User Email: `  +
                                  `<span class="card-title">${response["userData"][7][i]}</span>` +
                                `</div>` +
                              `</div>` +
                            `</div>`)

    }


    



  });



  let signupData = {
    email: email
  }

  // $.post("/getAllSignUpData", JSON.stringify(signupData))
  // .then(function(response) {
  //   console.log("get SignupData \t " + JSON.stringify(response));
    // console.log("get SignupData \t " + JSON.stringify(response["groupData"][1]));

    // if((response["groupData"][1]) == "PENDING"){

      // $("#NewRegistrationsTab").append(`<div class="col s12 m4">` +
      //                                     `<div class="card blue-grey darken-1">` +
      //                                       `<div class="card-content white-text">` +
      //                                         `<span class="card-title">New User Name</span>` +
      //                                       `</div>` +
      //                                       `<div class="card-action">` +
      //                                         `<a href="#">Accept</a>` +
      //                                         `<a href="#">Decline</a>` +
      //                                       `</div>` +
      //                                     `</div>` +
      //                                   `</div>`)
    // }
  // });

    function getData() {
    $.ajax({
        url: "/getAllSignUpData",
        method: "GET"
    }).then(function(response) {
        console.log("GET root worked fine\n",JSON.stringify(response));
        // $("#test1").append("<p style='font-weight: bold'> Type: " + response.tasks[0].description + "</p><br>");

      for(let i=0; i<response["signUpData"].length; i++){
        for(let j=0; j<response["signUpData"][i].length; i++){
            console.log("LOOOPING \t", response["signUpData"][i][6])

            if((response["signUpData"][i][6]) == "PENDING"){
            $("#NewRegistrationsTab").append(`<div class="col s12 m4 NewDiv" id=${response["signUpData"][i][1]}>` +
                                                `<div class="card blue-grey darken-1">` +
                                                  `<div class="card-content white-text">` +
                                                    `<span class="card-title">${response["signUpData"][i][0]}</span>` +
                                                    `<p id="applicantEmail">${response["signUpData"][i][1]}</p>` +
                                                    `<p>New User Registration Request<br></p>` +
                                                  `</div>` +
                                                  `<div class="card-action">` +
                                                    `<a href="#" id="handle-button">ACCEPT</a>` +
                                                    `<a href="#" id="handle-button">DECLINE</a>` +
                                                  `</div>` +
                                                `</div>` +
                                              `</div>`)
          }
          else if((response["signUpData"][i][6]) == "APPEALED"){
            $("#NewRegistrationsTab").append(`<div class="col s12 m4 NewDiv" id=${response["signUpData"][i][1]}>` +
                                                `<div class="card blue-grey darken-1">` +
                                                  `<div class="card-content white-text">` +
                                                    `<span class="card-title">${response["signUpData"][i][0]}</span>` +
                                                    `<p id="applicantEmail">${response["signUpData"][i][1]}</p>` +
                                                    `<p>${response["signUpData"][i][5]}</p>` +
                                                  `</div>` +
                                                  `<div class="card-action">` +
                                                    `<a href="#" id="handle-button">ACCEPT</a>` +
                                                    `<a href="#" id="handle-button">BLACKLIST</a>` +
                                                  `</div>` +
                                                `</div>` +
                                              `</div>`)
          }
        }
      }

    });
  };
  getData();


  $(document.body).on("click", "#handle-button", function(event) {

    console.log("BUTTON TEXT: ", $("#applicantEmail").text())

    let handleAppData = {
      response: $(this).text(), //acc dec bl
      applicantEmail: $("#applicantEmail").text()
    }
  
    $.post("/handleApplication", JSON.stringify(handleAppData))
    .then(function(response) {
          console.log(response["Message"])
          M.toast({html: response["Message"]})
          location.reload()
        }
      );

  });









  // <div class="col s12 m4">
  // <div class="card blue-grey darken-1">
  //   <div class="card-content white-text">
  //     <span class="card-title">New User Name</span>
  //     <p>This section contains basic information regarding the user.<br></p>
  //   </div>
  //   <div class="card-action">
  //     <a href="#">Accept</a>
  //     <a href="#">DECLINE</a>
  //   </div>
  // </div>
  // </div>




});