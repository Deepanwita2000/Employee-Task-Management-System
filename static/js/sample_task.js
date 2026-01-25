$(document).ready(function () {

    // Add new textarea
    $(document).on('click', '.add_more', function () {

        // Remove Add button from current row
        // $(this).remove();

        $('#text_box').append(`
            <div class="d-flex mb-2 field-row">
                <textarea type='text' class="form-control" name="task"  id="task" rows="1"  placeholder="Enter task"></textarea>
                <button type="button" class="btn btn-danger ms-2 remove_row">Remove</button>
            </div>
        `);
    });

    // Remove textarea
    $(document).on('click', '.remove_row', function () {
        $(this).closest('.field-row').remove();
    });

    // assign task
    $("#add_task_btn").click(function(e){
        e.preventDefault()
        // task=$("#task").val()
        let tasks = [];
        const domain= $("#domain").val()
        const proj_id= $("#proj_id").val()
        const manager_id= $("#manager_id").val()
        const end_date= $("#end_date").val()
        const status = $("#status").val()
       
            $('textarea[name="task"]').each(function () {
                const value = $(this).val().trim();
                if (value !== '') {
                    tasks.push(value);
                }
            });
         console.log(tasks);   // 👉 Array of all task values
          $.ajax({
            url:'/task2/view_sample/',
            method : 'POST',
            data : {
                tasks:tasks,
                domain:domain,
                proj_id:proj_id,
                manager_id:manager_id,
                end_date:end_date,
                status:status,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()

            },
            success: function(response){
                
                alert(response.message)
                $("#domain").val("")
                $("#end_date").val("")
                $("#task").val("")
            }
        })
    })

    // asssign employees
    $("#add_emp_btn").click(function(e){
        e.preventDefault()
        console.log("hello")
       
        const proj_id= $("#proj_id").val()
        const manager_id= $("#manager_id").val()
        const status = $("#status").val()
        const emp_id = $("#emp_id").val()
        console.log(emp_id)
          $.ajax({
            url:'/task2/assign_employee/',
            method : 'POST',
            data : {
                emp_id:emp_id,
                
                proj_id:proj_id,
                manager_id:manager_id,
                
                status:status,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()

            },
            success: function(response){
                alert(response.message)
                $("#emp_id").val("")
            }
        })
    })


    //--------------------------------- check Box ----------- 
       function updateProgress(points) {
    points = Math.min(points, 100);

    $('#progressBar')
        .css('width', points + '%')
        .attr('aria-valuenow', points);

    $('#progressText').text(points + '%');
}


    //    $('.points').on('change', function () {

    //     if (!this.checked) return;

    //     const checkbox = $(this);
    //     //  const checkbox = $(this);

    // const task   = checkbox.data('task');
    // const status = checkbox.data('status');
    // const employee = checkbox.data('employee');
    // const domain = checkbox.data('domain');
    // const project = checkbox.data('project');
    // // const point = $('#point').val()
    // const point = checkbox.val();

  
    // console.log(task, status, domain, project,employee,point);
       
    //     $.ajax({
    //         url: '/task2/progress/',
    //         type: 'POST',
    //         data: {
    //             task   : task,
    //             status : status,
    //             employee : employee,
    //             domain : domain,
    //             project : project,
    //             point : point,
    //             csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
    //         },
    //         success: function (response) {
    //             if (response.success) {
    //                 row.addClass('disabled-row');
    //                 row.find('input').prop('disabled', true);
    //             }
    //             alert(response.message)
    //             // $(".points").text(response.context['total_points'])
    //             updateProgress(response.total_points);

    //             // $(".points").html(``)
    //         },
    //         error: function () {
    //             alert('Something went wrong');
    //         }
    //     });
    // });





$(document).on('change', '.points', function () {

    if (!this.checked) return;

    const checkbox = $(this);
    const row = checkbox.closest('tr');

    const task     = checkbox.data('task');
    const status   = checkbox.data('status');
    const employee = checkbox.data('employee');
    const domain   = checkbox.data('domain');
    const project  = checkbox.data('project');
    const point    = checkbox.val();

    $.ajax({
        url: '/task2/progress/',
        type: 'POST',
        data: {
            task: task,
            status: status,
            employee: employee,
            domain: domain,
            project: project,
            point: point,
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').first().val()
        },
        success: function (response) {
            if (response.success) {

                // ✅ Disable row
                row.find('input').prop('disabled', true);

                // ✅ OPTION 1: Hide row
                row.fadeOut(400);

                // ✅ OPTION 2 (instead of fadeOut): Just disable visually
                // row.css({ opacity: '0.5', pointerEvents: 'none' });

                updateProgress(response.total_points);
            } else {
                checkbox.prop('checked', false);
                alert(response.message);
            }
        },
        error: function () {
            checkbox.prop('checked', false);
            alert('Something went wrong');
        }
    });
});







    //--------------------------------------------------chat Bot
    //  $(document).on("submit", "#timelineForm", function (e) {
    //         e.preventDefault();
    //         let team = [];
    //         $(".team-member").each(function () {
    //             team.push({
    //                 name: $(this).data("name"),
    //                 role: $(this).data("role"),
    //                 experience: $(this).data("experience"),
    //                 domain: $(this).data("domain")
    //             });
    //         });
        
    //         console.log($("#expected_timeline").val(),)
    //         console.log(team)

    //         $.ajax({
    //             url: "/task2/timeline_ai/",
    //             method: "POST",
    //             data: {
    //                 project_description: $("#project_description").val(),
    //                 expected_timeline: $("#expected_timeline").val(),
    //                 team: JSON.stringify(team),
    //                 csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
    //             },
    //             beforeSend: function () {
    //                 $("#timelineResult").html("loading...");
                   
    //             },
    //             success: function (res) {
    //                 if (!res.success) {
    //                     $("#timelineResult").html("Error generating timeline");
    //                     return;
    //                 }

    //                 let html = "<h4>Phase-wise Timeline</h4><pre>" +
    //                     JSON.stringify(res.data.phase_wise, null, 2) +
    //                     "</pre><h4>Parallel Timeline</h4><pre>" +
    //                     JSON.stringify(res.data.parallel, null, 2) +
    //                     "</pre>";

    //                 $("#timelineResult").html(html);
    //             }
    //         });
    //     });

});
