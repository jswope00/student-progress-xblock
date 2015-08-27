function StdProgXBlock(runtime, element) {
  $(element).find('.save-button').bind('click', function() {
    var handlerUrl = runtime.handlerUrl(element, 'studio_submit');
    console.log($(element).find('input[id=course_progress]')[0].checked);
    console.log($(element).find('input[id=section_progress]')[0].checked);
    var data = {
      course_progress : $(element).find('input[id=course_progress]')[0].checked,
      section_progress : $(element).find('input[id=section_progress]')[0].checked
    };
    runtime.notify('save', {state: 'start'});
    $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
      runtime.notify('save', {state: 'end'});
    });
  });

  $(element).find('.cancel-button').bind('click', function() {
    runtime.notify('cancel', {});
  });
}