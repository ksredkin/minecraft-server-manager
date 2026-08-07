const ConfirmDialog = ({onConfirm, onCancel, dialog = {show: false, title: "", description: "", confirm_text: "", confirm_type: "success"}}) => {
  if (!dialog.show) return
  return (<div className="confirm-dialog-background">
    <div className="confirm-dialog">
      <h3 className="confirm-dialog-header-text">{dialog.title}</h3>
      <h5 className="confirm-dialog-header-description">{dialog.description}</h5>
      <div className="confirm-dialog-buttons-div">
        <button className={"confirm-dialog-confirm-button confirm-dialog-confirm-button-" + dialog.confirm_type} onClick={onConfirm}>{dialog.confirm_text}</button>
        <button className="confirm-dialog-cancel-button" onClick={onCancel}>Отмена</button>
      </div>
    </div>
  </div>)
}

export default ConfirmDialog
