// $(document).ready(function(){
//     console.log("AJAX: comment")
//     $("#comment-btn").click(function(e){
//         e.preventDefault()
//         console.log("comment clicked !!")
       
//         com_id = $("#comment-btn").val()
//         com_text = $("#comment").val()
//         console.log(com_id , com_text)
//         $.ajax({
//             url : `/comment/create_comment_pro/`,
//             method : "POST",
//             data: {
//                      com_id : com_id,
//                      com_text : com_text,
//                      csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
//             },
//             success : function(response){
//                 $('#comment_box').html(response.comments);
//             }
           

//         })

//     })
// })







// #############################333
$(document).ready(function(){
    console.log("AJAX: comment")
    $("#comment-btn").click(function(e){
        e.preventDefault()
        console.log("comment clicked !!")
       
        com_id = $("#comment-btn").val()
        com_text = $("#comment").val()
        console.log(com_id , com_text)
        $.ajax({
            url : `/comment/create/${com_id}/`,
            method : "POST",
            data: {
                     com_id : com_id,
                     com_text : com_text,
                     csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success : function(response){
                $('#comment_box').html(response.comments);
            }
           

        })

    })


// $(document).on("click", ".complete_btn", function(e) {
//     e.preventDefault();

//     const taskID = $(this).data("id");
//     console.log("Completed task:", taskID);

//     $.ajax({
//         url: `/task/update_status/`,
//         type: "POST",
//         data: {
//             taskID: taskID,
//             csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
//         },
//         success: function(response) {
//             $("#acknowledge")
//                 .text("Task saved successfully!")
//                 .css("color", "green")
//                 .fadeIn().delay(2000).fadeOut();
//         },
//         error: function(xhr) {
//             const error = xhr.responseJSON?.error || "Something went wrong.";
//             $('#message').html('<div class="alert alert-danger">' + error + '</div>');
//         }
//     });

//     $(this).text('Completed');
// });





})