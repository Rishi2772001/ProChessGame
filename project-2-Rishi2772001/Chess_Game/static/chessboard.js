function movePiece() {
    let src = $('#src').val();
    let dst = $('#dst').val();
  
    if (src && dst) {
        let sourceElement = $('#' + src);
        let destinationElement = $('#' + dst);
  
        if (sourceElement.length && destinationElement.length) {
            destinationElement.html(sourceElement.html());
            sourceElement.html("&nbsp;");
        }
    }
  }
  function resetBoard() {
    location.reload();
  }
  