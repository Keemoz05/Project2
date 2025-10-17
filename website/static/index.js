function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

function deleteItem(lostitemid) {
  fetch("/delete-lostitem", {
    method: "POST",
    body: JSON.stringify({ lostitemid: lostitemid }),
  }).then((_res) => {
    window.location.href = "/user-settings"; ///user-settings
  });
}