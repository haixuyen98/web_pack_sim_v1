var currentCustomizeWebhookUrlEditItem = null;

function addCustomizeWebhookUrl(__this) {
  $('.fm-customize').find('input[name="webhook_url"]').val('');
  $('.fm-customize').find('textarea[name="content"]').val('');
  $('#customize-modal').modal('show');
}

function editCustomizeWebhookUrl(__this) {
  currentCustomizeWebhookUrlEditItem = __this.closest('.item-customize-webhook-url');
  $('.fm-customize').find('input[name="uuid"]').val(currentCustomizeWebhookUrlEditItem.attr('data-uuid'));
  $('.fm-customize').find('input[name="webhook_url"]').val(currentCustomizeWebhookUrlEditItem.attr('data-webhook-url'));
  $('.fm-customize').find('textarea[name="content"]').val(currentCustomizeWebhookUrlEditItem.attr('data-content'));
  $('#customize-modal').modal('show');
}

function deleteCustomizeWebhookUrl(__this){
  currentCustomizeWebhookUrlEditItem = __this.closest('.item-customize-webhook-url');
  $('#id_del_uuid').val(currentCustomizeWebhookUrlEditItem.attr('data-uuid'));
  $('#changelist-form').submit()
}
