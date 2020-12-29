function init(){
  $('.btn-map-delete').click(function(){
    var action = $(this).data('actiondelete');
    $('#confirmationModal').modal();
    $('.form-map-delete').attr('action', action);
  });
}

document.addEventListener('DOMContentLoaded', function() {
  init();
});