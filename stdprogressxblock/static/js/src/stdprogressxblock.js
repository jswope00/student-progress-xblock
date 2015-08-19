/* Javascript for StdProgXBlock. */
function StdProgXBlock(runtime, element) {

    var course_id;

    function updateCount(result) {
        $('.count', element).text(result.count);
        $('.data', element).text(result.course_progress_percent);
        $('.itemscompeted', element).text(result.course_progress);
        console.log("Update count clicked");
    }

    var handlerUrl = runtime.handlerUrl(element, 'increment_count');

    $('p', element).click(function(eventObject) {
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({
                "hello": "world"
            }),
            success: updateCount
        });
    });

    $(function($) {
        /* Here's where you'd do things on page load. */
        data = window.location.pathname;
        var start_position = data.indexOf("/", data.indexOf("/", data.indexOf("/") + 1) + 1);
        var end_position = data.indexOf("/", data.indexOf("/", data.indexOf("/", data.indexOf("/") + 1) + 1) + 1);
        course_id = data.substring(start_position + 1, end_position);
        console.log(data);
        console.log(course_id);
    });
}
