const stop_launch_class_name = '.stop_launch'
$(document).on('click', stop_launch_class_name, function (event) {
    event.preventDefault();
    const task_id = event.target.id;
    const element = $(`#${task_id}${stop_launch_class_name}`);
    $.ajax({
        type: 'GET',
        url: $(event.target).attr('href'),
        success: function (json) {
            if (json.status == 1) {
                element.removeClass('btn-success').addClass('btn-warning');
                element.text('Остановить');
            }
            if (json.status == 0) {
                element.removeClass('btn-warning').addClass('btn-success');
                element.text('Запустить')

            } 
        },
        error: function (xhr, errmsg, err) {
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            element.text('Ошибка');
        }
    });

});