const delete_class_name = '.delete'
$(document).on('click', delete_class_name, function (event) {
    event.preventDefault();
    const task_id = event.target.id;
    const element = $(`#${task_id}${delete_class_name}`);
    $.ajax({
        type: 'GET',
        url: $(event.target).attr('href'),
        error: function (xhr, errmsg, err) {
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            element.text('Ошибка');
        }
    });

});