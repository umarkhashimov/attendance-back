

function markStudent(status, stid) {
    const studentData = document.querySelector(`.students-attendance-list tr[stid='${stid}']`)
    studentData.setAttribute('status', status);
    studentData.querySelector(`#statusInp${stid}`).value = status;
}


function unmarkStudent(stid) {
    const studentData = document.querySelector(`.students-attendance-list tr[stid='${stid}']`)
    studentData.setAttribute('status', '');
    studentData.querySelector(`#statusInp${stid}`).value = '';
}