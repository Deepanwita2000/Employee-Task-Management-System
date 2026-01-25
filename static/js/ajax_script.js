$(document).ready(function(){
    console.log("ajax is ready!!")

//*****************************************  User Registration Login  *************************************************
    $('#cardForm').hide();

    $('#hide').click(function(e){
        $('#cardForm').hide();
    })

    $('#show').click(function(e){
        $('#cardForm').show();
    })

    $(".task-edit-btn").click(function(e){
         $('#cardForm').show();
    })

    $("#task-btn").click(function(e){
         $('#cardForm').hide();
    })

    // image preview
    $("#user_image").on("change", function (event) {
        const file = event.target.files[0];
        const preview = $("#imagePreview");  

        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                preview.attr("src", e.target.result).show();
            };
            reader.readAsDataURL(file);
        } else {
            preview.attr("src", "").hide();
        }
    });

      // Register user
    $("#signup_btn").click(function (e) {
        e.preventDefault();
        console.log("Signing up...");
        role= $("#role").val(),
        console.log(role)
        if (role === 'manager')
            rolePart='manager'
        else
            rolePart='employee'
        console.log(rolePart)
        const formData = new FormData($("#signupForm")[0]);


        $.ajax({
                url: `/account/register_${rolePart}/`,
                method: "POST",
                data: formData,
                processData: false,  // Required for FormData
                contentType: false,
                beforeSend: function () {
                    $("#spinner-overlay").show();       // Show spinner overlay before request is sent
                },
                success: function (response) {
                    $("#acknowledge").text(response.message)
                        .css("color", "green")
                        .fadeIn().delay(5000).fadeOut();

                    // Redirect to login page after 7 seconds
                    setTimeout(() => {
                        window.location.href = response.redirect_url;
                    }, 7000);
                },
                error: function (xhr) {
                    const errorMsg = xhr.responseJSON?.error || "Something went wrong.";
                    
                    $("#acknowledge").html(`<div class="alert alert-danger">${errorMsg}</div>`);
                },
                complete: function () {
                    // Always hide spinner overlay after request finishes (success or error)
                    $("#spinner-overlay").hide();
                }
        });
    });

    // Login user
    $("#login_btn").click(function (e) {
        e.preventDefault();
        console.log("🔐 Logging in...");

        $.ajax({
        url: "/account/sample_login/",
        method: "POST",
        data: {
            email: $("#email").val(),
            password: $("#password").val(),
            csrfmiddlewaretoken : $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
            $("#acknowledge").text("User login successfully!")
                             .css("color", "green")
                             .fadeIn().delay(2000).fadeOut();

            setTimeout(() => {
                window.location.href = response.redirect_url;
            }, 1000);
        },
        error: function (xhr) {
            const errorMsg = xhr.responseJSON?.error || 
                             xhr.responseJSON?.message ||
                             "Something went wrong.";
            console.log(xhr.error);               
            console.log(xhr.message);               
            console.log(errorMsg);               
            $("#error_message").html(`<span class="text-danger">${errorMsg}</span>`)
                               .show()
                               .fadeIn().delay(2000).fadeOut();
        },
        });
    });



    // otp
    $("#otp_btn").click(function (e) {
        e.preventDefault();
        console.log("🔐 Logging in...");
        otp= $("#otp").val()
        // org_otp= $("#org_otp").val()
        console.log(otp)
        $.ajax({
        url: "/account/add_otp/",
        method: "POST",
        data: {
            otp: otp,
          
            csrfmiddlewaretoken : $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
            if (response.status === "success") {
        $("#acknowledge").text("User login successfully!")
                         .css("color", "green")
                         .fadeIn().delay(2000).fadeOut();

        setTimeout(() => {
            window.location.href = response.redirect_url;
        }, 1000);

    } else {
        $("#error_otp_message")
            .html(`<span class="text-danger">${response.message}</span>`)
            .show()
            .fadeIn().delay(2000).fadeOut();
    }
        },
        error: function (xhr) {
            const errorMsg = xhr.responseJSON?.error || 
                             xhr.responseJSON?.message ||
                             "Something went wrong.";
            console.log(xhr.error);               
            console.log(xhr.message);               
            console.log(errorMsg);               
            $("#error_otp_message").html(`<span class="text-danger">${errorMsg}</span>`)
                               .show()
                               .fadeIn().delay(2000).fadeOut();
        },
        });
    });

    

    $("#resend_btn").click(function (e) {
        e.preventDefault();
        console.log("🔐 resend in...");
        
        $.ajax({
        url: "/account/resend_otp/",
        method: "POST",
        data: {
           
          
            csrfmiddlewaretoken : $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
            alert(response.success)
        

    },
    
        error: function (xhr) {
            const errorMsg = xhr.responseJSON?.error || 
                             xhr.responseJSON?.message ||
                             "Something went wrong.";
            console.log(xhr.error);               
            console.log(xhr.message);               
            console.log(errorMsg);               
            $("#error_otp_message").html(`<span class="text-danger">${errorMsg}</span>`)
                               .show()
                               .fadeIn().delay(2000).fadeOut();
        },
        });
    });

//*****************************************  Task  *************************************************
    // task assignment
    $("#task-btn").click(function(e){
        e.preventDefault()
        console.log("clicked")
        const task_id = $("#task_id").val()
        // const event_id = $("#event_id").val();
        console.log(task_id)
        
        $.ajax({
                url : task_id ? `/task/edit_task/${task_id}/`:`/task/add_task/`,
                type : "POST",
                data :{
                    title : $("#title").val(),
                    description : $("#description").val(),
                    status : $("#status").val(),
                    employee : $("#employee").val(),
                    // emp_id : $("#emp_id").val(),
                    project : $("#project").val(),
                    end_date : $("#end_date").val(),
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()

                },
                success : function(response){
                            $("#acknowledge").text("task saved successfully!")
                                .css("color", "green")
                                .fadeIn().delay(2000).fadeOut();
                                $("#title").val(""),
                                $("#description").val(""),
                                $("#status").val(""),
                                $("#employee").val(""),
                                 $("#list_of_tasks").html(response.tasks);
                   
                        },
                
                error: function (error) {
                        const errorMessage = error.responseJSON?.message || "An error occurred.";
                        // alert(errorMessage)
                        $("#acknowledge").text(errorMessage)
                            .css("color", "red")
                            .fadeIn().delay(2000).fadeOut();
                    }
        
        })

    })

    // edit task
    $(document).on("click", ".task-edit-btn", function () {
        console.log("📝 task event...");
      
        const taskID = $(this).data("id");
        const tasktTitle = $(this).data("title");
        const tasktDescription = $(this).data("description");
        const taskStatus = $(this).data("status");
        const emp_id = $(this).data("assigned_to-id");
        console.log(emp_id)

        $("#task_id").val(taskID);
        $("#title").val(tasktTitle);
        $("#description").val(tasktDescription);
        $("#status").val(taskStatus);
        $("#employee").val(emp_id);
        // $("#event-title").text("Update Event");
        // $("#event-save-btn").text("Update");

    });

    // delete task
     $(document).on("click", ".task-delete-btn", function () {
        
        const task_id = $(this).data("id")
        console.log(task_id)
        if (!confirm("Are you sure you want to delete this task?")) {
            return;
        }
  
        $.ajax({
            url: `/task/delete_task/${task_id}/`,
            type: "POST",
            data: {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function (response) {
                $("#acknowledge").text("Task deleted successfully!")
                    .css("color", "red")
                    .fadeIn().delay(2000).fadeOut();

                // Refresh table after delete
                  $("#list_of_tasks").html(response.tasks);
               
                
            },
            error: function (xhr) {
                let error = xhr.responseJSON?.error || "Something went wrong.";
                $('#message').html('<div class="alert alert-danger">' + error + '</div>');
            }
        });
    })


//************************************ Renew update status('compelete' , 'in progress') **********************************

   //complete
   $(document).on("click", ".complete-btn", function(e) {
        e.preventDefault();

        let taskID = $(this).data("id");
        let status  = $(this).data("status");
        
        console.log("task:", taskID,status);

        $.ajax({
            url: `/task/update_status/${taskID}/${status}/`,
            method: "POST",
            data: {
                taskID: taskID,
                current_status : status,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                $("#acknowledge")
                    .text("Task saved successfully!")
                    .css("color", "green")
                    .fadeIn().delay(2000).fadeOut();
                    console.log("success")
                    console.log(response)
                
                 $("#list_of_tasks").html(response.tasks);
                
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.error || "Something went wrong.";
                $('#message').html('<div class="alert alert-danger">' + error + '</div>');
            }
        });
    })

    //progress
    $(document).on("click", ".progress-btn", function(e) {
        e.preventDefault();

        let taskID = $(this).data("id");
        let status  = $(this).data("status");
        let progress_value  = $(this).data("progress_value");
        console.log(progress_value)
        console.log("task:", taskID,status);

        $.ajax({
            url: `/task/update_status/${taskID}/${status}/`,
            method: "POST",
            data: {
                taskID: taskID,
                current_status : status,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                $("#acknowledge")
                    .text("Task saved successfully!")
                    .css("color", "green")
                    .fadeIn().delay(2000).fadeOut();
                    console.log("success")
                    console.log(response)
                // if (response.success) {
                //     alert("Status updated successfully!");
                //     location.reload();  // reload page to show updated status

                // }
                $("#list_of_tasks").html(response.tasks);
                $('#status_value').html(progress_value)
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.error || "Something went wrong.";
                $('#message').html('<div class="alert alert-danger">' + error + '</div>');
            }
        });
    })

    // Show progress value immediately without reload
    $(document).on("click", ".mark_btn", function(e) {
         console.log("progress marked")
            e.preventDefault()
            let value = $("#progress_value").val()
            $("#display_value").text(`${value}%`)
            let task_id = $(this).data("id")
            console.log(value , task_id)

            console.log(value, task_id);
            
                $.ajax({
                    url : `/task/analyze_progress/`,
                    method : "POST",
                    data :{
                        progress_value : value,
                        task_id :task_id,
                        
                        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()

                    },
                    success : function(response){
                                $("#acknowledge").text("task saved successfully!")
                                    .css("color", "green")
                                    .fadeIn().delay(2000).fadeOut();
                                    $("#title").val(""),
                                    $("#description").val(""),
                                    $("#status").val(""),
                                    $("#emp_email").val(""),
                                    alert(response.message)
                        
                            },
                })
    })

    
  

    // ------------------ chat BOT ----------------------------------------
    //  $("#chat_btn").click(function(e){
    //     e.preventDefault()
    //     console.log("clicked !!")
    //     console.log( $("#question").val().trim())
    //     $.ajax({
    //         url : `/task2/timeline_ai/`,
    //         method :"POST",
    //         data :{
    //             quest : $("#question").val(),
    //             csrfmiddlewaretoken :$("input[name=csrfmiddlewaretoken]").val()
    //         },
    //          beforeSend: function () {
    //             $("#spinner-overlay").show();       // Show spinner overlay before request is sent
    //         },
    //         success : function(response){
    //            res =  $("#reply").text()
    //             console.log(res)
    //             $("#reply").html(response.answere); 
                
  
    //         },
    //         complete: function () {
    //             // Always hide spinner overlay after request finishes (success or error)
    //             $("#spinner-overlay").hide();
    //         }
    //     })
    // })





$("#timelineForm").submit(function(e){
    e.preventDefault();

    // Gather team data
    let team = [];
    $(".team-member").each(function(){
        team.push({
            name: $(this).data("name"),
            role: $(this).data("role"),
            experience: $(this).data("experience"),
            domain: $(this).data("domain")
        });
    });

    $.ajax({
       url : `/task2/timeline_ai/`, // make sure your URL name matches
        method: "POST",
        data: {
            project_description: $("#project_description").val(),
            expected_timeline: $("#expected_timeline").val(),
            team: JSON.stringify(team),
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
        },
        beforeSend: function(){
            $("#spinner-overlay").show();
        },
        success: function(response){
            $("#timelineResult").html("<pre>" + response.timeline + "</pre>");
        },
        error: function(xhr){
            $("#timelineResult").html("Error generating timeline");
            console.error(xhr.responseJSON);
        },
        complete: function(){
            $("#spinner-overlay").hide();
        }
    });
});






// // filter employees with domain
//    $("#domain").click(function(event){
//         event.preventDefault()
//         console.log("doamin clicked")

//         const domain = $("#domain").val()
//         console.log(domain)
//         const csrfToken = $("input[name=csrfmiddlewaretoken]").val();

//         $.ajax({
//             url:`/task2/domain_category/`,
//             method : "POST",
//             data :{
//                 domain : domain,
//                 csrfmiddlewaretoken : csrfToken
//             },
//             success:function(response){
//                   $("#all_employees").html(response.data);
//             }

//         })



//     })

$("#domain").on("change", function () {
    const domain = $(this).val();
    console.log(domain)
    if (!domain) return;   // stop empty request
    let url = "";
    let method = "";
    const csrfToken = $("input[name=csrfmiddlewaretoken]").val();
    if (domain === 'all') {
    // your logic when domain is 'all'
            url = "/task2/all_employees/"
            method="POST"
           
        } else {
            // your logic when domain is NOT 'all'
            url= "/task2/domain_category/"
                method="POST"
        }


    $.ajax({
        url: url,
        method: method,
        data: {
            domain: domain,
            csrfmiddlewaretoken: csrfToken
        },
        success: function (response) {
            $("#all_employees").html(response.data);
            // $("#count").text(`emp count: ${response.emp_count}`);
            // $("#count").text(`emp count: ${response.designation}`);
            if (response.designation === 0)
            {
                $("#count").text("");
                console.log(response.designation , response.emp_count)
            }
            else{
                $("#count").text(`${response.designation} : ${response.emp_count}`);
                console.log(response.designation , response.emp_count)
            }
            
            
        }
    });
});















})